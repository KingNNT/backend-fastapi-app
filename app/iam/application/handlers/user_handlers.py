"""User command handlers - execute user write operations."""

from uuid import UUID

from app.iam.application.commands.user.create_user import CreateUserCommand
from app.iam.application.commands.user.delete_user import DeleteUserCommand
from app.iam.application.commands.user.update_user import UpdateUserCommand
from app.iam.application.interfaces.password_hasher import IPasswordHasher
from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork
from app.iam.domain.user.aggregate import UserAggregate
from app.iam.domain.user.domain_service import UserDomainService
from app.iam.domain.user.exceptions import UserNotFound
from app.iam.domain.user.value_objects import Email, Username
from app.shared.domain.ids.user_id import UserId


class CreateUserHandler:
    """Handler for CreateUserCommand.

    Uses Unit of Work for transaction management and repository access.
    Delegates domain validation to UserDomainService.
    """

    def __init__(
        self,
        password_hasher: IPasswordHasher,
    ) -> None:
        """Initialize handler with password hasher.

        Args:
            password_hasher: Service for hashing passwords.
        """
        self._password_hasher = password_hasher

    async def handle(self, command: CreateUserCommand, uow: IIamUnitOfWork) -> str:
        """Execute the create user command and return user ID.

        Args:
            command: The create user command containing user data.
            uow: Unit of Work for transaction management.

        Returns:
            The created user's ID as string.

        Raises:
            UserAlreadyExists: If email or username already exists.
        """
        email = Email(command.email)
        username = Username(command.username)

        # Validate uniqueness via domain service
        await UserDomainService.validate_new_user(email, username, uow.users_read)

        # Hash password
        hashed_password = self._password_hasher.hash(command.password)

        # Create aggregate
        aggregate = UserAggregate.create(
            email=email,
            username=username,
            password=hashed_password,
            full_name=command.full_name,
        )

        # Persist via UoW
        await uow.users.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return aggregate.id_str


class UpdateUserHandler:
    """Handler for UpdateUserCommand.

    Uses Unit of Work for transaction management and repository access.
    Delegates domain validation to UserDomainService.
    """

    def __init__(
        self,
        password_hasher: IPasswordHasher,
    ) -> None:
        """Initialize handler with password hasher.

        Args:
            password_hasher: Service for hashing passwords.
        """
        self._password_hasher = password_hasher

    async def handle(self, command: UpdateUserCommand, uow: IIamUnitOfWork) -> str:
        """Execute the update user command and return user ID.

        Args:
            command: The update user command containing update data.
            uow: Unit of Work for transaction management.

        Returns:
            The updated user's ID as string.

        Raises:
            UserNotFound: If user doesn't exist.
            UserAlreadyExists: If new email/username already taken.
        """
        # Get existing user
        user_id = UserId.from_string(command.user_id)
        aggregate = await uow.users_read.get_by_id(user_id)
        if aggregate is None:
            raise UserNotFound(command.user_id)

        # Parse new values if provided
        new_email = Email(command.email) if command.email else None
        new_username = Username(command.username) if command.username else None

        # Validate uniqueness via domain service
        await UserDomainService.validate_user_update(
            user_id=command.user_id,
            user_read_repo=uow.users_read,
            email=new_email,
            username=new_username,
        )

        # Apply updates
        if new_email is not None:
            aggregate.update_email(new_email)

        if new_username is not None:
            aggregate.update_profile(username=new_username)

        if command.full_name is not None:
            aggregate.update_profile(full_name=command.full_name)

        if command.password is not None:
            hashed_password = self._password_hasher.hash(command.password)
            aggregate.update_password(hashed_password)

        # Persist via UoW
        await uow.users.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return aggregate.id_str


class DeleteUserHandler:
    """Handler for DeleteUserCommand.

    Uses Unit of Work for transaction management and repository access.
    """

    def __init__(self) -> None:
        """Initialize handler (no dependencies needed)."""
        pass

    async def handle(self, command: DeleteUserCommand, uow: IIamUnitOfWork) -> bool:
        """Execute the delete user command.

        Args:
            command: The delete user command.
            uow: Unit of Work for transaction management.

        Returns:
            True if deletion was successful.

        Raises:
            UserNotFound: If user doesn't exist.
        """
        # Get existing user
        user_id = UserId.from_string(command.user_id)
        aggregate = await uow.users_read.get_by_id(user_id)
        if aggregate is None:
            raise UserNotFound(command.user_id)

        # Soft delete
        deleted_by = UUID(command.deleted_by) if command.deleted_by else None
        aggregate.soft_delete(deleted_by=deleted_by)

        # Persist via UoW
        await uow.users.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return True
