"""User domain service - cross-entity domain logic."""

from app.core.domain.aggregates.user import UserAggregate
from app.core.domain.exceptions.user import UserAlreadyExists
from app.core.domain.exceptions.validation import BusinessRuleViolation
from app.core.domain.repositories.user import IUserReadRepository
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.username import Username


class UserDomainService:
    """Domain service for user-related cross-entity operations.

    Contains domain logic that doesn't naturally fit in an entity or aggregate.
    This service is stateless - all methods receive dependencies as parameters.

    Note: Uses IUserReadRepository (domain interface) instead of IUnitOfWork
    to maintain proper layer boundaries (domain should not depend on application).
    """

    @staticmethod
    async def ensure_email_unique(
        email: Email,
        user_read_repo: IUserReadRepository,
        exclude_user_id: str | None = None,
    ) -> None:
        """Ensure the email is unique across all users.

        Args:
            email: The email to check.
            user_read_repo: Repository for reading user data.
            exclude_user_id: Optional user ID to exclude (for updates).

        Raises:
            UserAlreadyExists: If email is already taken.
        """
        existing_user = await user_read_repo.get_by_email(email)
        if existing_user is not None:
            if exclude_user_id is None or existing_user.id_str != exclude_user_id:
                raise UserAlreadyExists(field_name="email", field_value=str(email))

    @staticmethod
    async def ensure_username_unique(
        username: Username,
        user_read_repo: IUserReadRepository,
        exclude_user_id: str | None = None,
    ) -> None:
        """Ensure the username is unique across all users.

        Args:
            username: The username to check.
            user_read_repo: Repository for reading user data.
            exclude_user_id: Optional user ID to exclude (for updates).

        Raises:
            UserAlreadyExists: If username is already taken.
        """
        existing_user = await user_read_repo.get_by_username(username)
        if existing_user is not None:
            if exclude_user_id is None or existing_user.id_str != exclude_user_id:
                raise UserAlreadyExists(
                    field_name="username", field_value=str(username)
                )

    @staticmethod
    async def validate_new_user(
        email: Email,
        username: Username,
        user_read_repo: IUserReadRepository,
    ) -> None:
        """Validate a new user can be created with the given email and username.

        Args:
            email: The email for the new user.
            username: The username for the new user.
            user_read_repo: Repository for reading user data.

        Raises:
            UserAlreadyExists: If email or username is already taken.
        """
        await UserDomainService.ensure_email_unique(email, user_read_repo)
        await UserDomainService.ensure_username_unique(username, user_read_repo)

    @staticmethod
    async def validate_user_update(
        user_id: str,
        user_read_repo: IUserReadRepository,
        email: Email | None = None,
        username: Username | None = None,
    ) -> None:
        """Validate user update doesn't violate uniqueness constraints.

        Args:
            user_id: The ID of the user being updated.
            user_read_repo: Repository for reading user data.
            email: Optional new email to validate.
            username: Optional new username to validate.

        Raises:
            UserAlreadyExists: If new email or username is already taken.
        """
        if email is not None:
            await UserDomainService.ensure_email_unique(
                email, user_read_repo, exclude_user_id=user_id
            )
        if username is not None:
            await UserDomainService.ensure_username_unique(
                username, user_read_repo, exclude_user_id=user_id
            )

    @staticmethod
    def can_transfer_ownership(
        from_user: UserAggregate,
        to_user: UserAggregate,
    ) -> bool:
        """Check if ownership can be transferred from one user to another.

        Both users must be active and not deleted.

        Args:
            from_user: The user transferring ownership.
            to_user: The user receiving ownership.

        Returns:
            True if transfer is allowed.

        Raises:
            BusinessRuleViolation: If transfer is not allowed.
        """
        if not from_user.user.is_active:
            raise BusinessRuleViolation.with_rule(
                rule_name="ownership_transfer",
                message="Cannot transfer ownership from inactive user",
            )
        if not to_user.user.is_active:
            raise BusinessRuleViolation.with_rule(
                rule_name="ownership_transfer",
                message="Cannot transfer ownership to inactive user",
            )
        return True
