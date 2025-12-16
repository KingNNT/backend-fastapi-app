"""User command handlers - execute user write operations."""

from typing import Protocol
from uuid import UUID

from app.core.application.commands.user.create_user import CreateUserCommand
from app.core.application.commands.user.delete_user import DeleteUserCommand
from app.core.application.commands.user.update_user import UpdateUserCommand
from app.core.application.interfaces.event_bus import IEventBus
from app.core.domain.aggregates.user import UserAggregate
from app.core.domain.exceptions.user import UserNotFound
from app.core.domain.repositories.user import IUserRepository
from app.core.domain.services.user_domain_service import UserDomainService
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.user_id import UserId
from app.core.domain.value_objects.username import Username


class IPasswordHasher(Protocol):
    """Interface for password hashing."""

    def hash(self, password: str) -> str:
        """Hash a password."""
        ...

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        ...


class CreateUserHandler:
    """Handler for CreateUserCommand."""

    def __init__(
        self,
        repository: IUserRepository,
        domain_service: UserDomainService,
        event_bus: IEventBus,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._repository = repository
        self._domain_service = domain_service
        self._event_bus = event_bus
        self._password_hasher = password_hasher

    async def handle(self, command: CreateUserCommand) -> str:
        """Execute the create user command and return user ID."""
        email = Email(command.email)
        username = Username(command.username)

        # Validate uniqueness using domain service
        await self._domain_service.validate_new_user(email, username)

        # Hash password
        hashed_password = self._password_hasher.hash(command.password)

        # Create aggregate
        aggregate = UserAggregate.create(
            email=email,
            username=username,
            password=hashed_password,
            full_name=command.full_name,
        )

        # Persist
        await self._repository.save(aggregate)

        # Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)
        aggregate.clear_events()

        return aggregate.id_str


class UpdateUserHandler:
    """Handler for UpdateUserCommand."""

    def __init__(
        self,
        repository: IUserRepository,
        domain_service: UserDomainService,
        event_bus: IEventBus,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._repository = repository
        self._domain_service = domain_service
        self._event_bus = event_bus
        self._password_hasher = password_hasher

    async def handle(self, command: UpdateUserCommand) -> str:
        """Execute the update user command and return user ID."""
        # Get existing user
        user_id = UserId.from_string(command.user_id)
        aggregate = await self._repository.get_by_id(user_id)
        if aggregate is None:
            raise UserNotFound(command.user_id)

        # Update email if provided
        if command.email is not None:
            new_email = Email(command.email)
            await self._domain_service.ensure_email_unique(
                new_email, exclude_user_id=command.user_id
            )
            aggregate.update_email(new_email)

        # Update username if provided
        if command.username is not None:
            new_username = Username(command.username)
            await self._domain_service.ensure_username_unique(
                new_username, exclude_user_id=command.user_id
            )
            aggregate.update_profile(username=new_username)

        # Update full name if provided
        if command.full_name is not None:
            aggregate.update_profile(full_name=command.full_name)

        # Update password if provided
        if command.password is not None:
            hashed_password = self._password_hasher.hash(command.password)
            aggregate.update_password(hashed_password)

        # Persist
        await self._repository.save(aggregate)

        # Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)
        aggregate.clear_events()

        return aggregate.id_str


class DeleteUserHandler:
    """Handler for DeleteUserCommand."""

    def __init__(
        self,
        repository: IUserRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: DeleteUserCommand) -> bool:
        """Execute the delete user command."""
        # Get existing user
        user_id = UserId.from_string(command.user_id)
        aggregate = await self._repository.get_by_id(user_id)
        if aggregate is None:
            raise UserNotFound(command.user_id)

        # Soft delete
        deleted_by = UUID(command.deleted_by) if command.deleted_by else None
        aggregate.soft_delete(deleted_by=deleted_by)

        # Persist
        await self._repository.save(aggregate)

        # Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)
        aggregate.clear_events()

        return True
