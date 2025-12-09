"""User domain service - cross-entity domain logic."""

from typing import Optional

from app.core.domain.aggregates.user import UserAggregate
from app.core.domain.exceptions.user import UserAlreadyExists
from app.core.domain.exceptions.validation import BusinessRuleViolation
from app.core.domain.repositories.user import IUserReadRepository
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.username import Username


class UserDomainService:
    """
    Domain service for user-related cross-entity operations.
    Contains domain logic that doesn't naturally fit in an entity or aggregate.
    """

    def __init__(self, user_read_repository: IUserReadRepository) -> None:
        self._user_read_repository = user_read_repository

    async def ensure_email_unique(
        self,
        email: Email,
        exclude_user_id: Optional[str] = None,
    ) -> None:
        """
        Ensure the email is unique across all users.
        Raises UserAlreadyExists if email is taken.
        """
        existing_user = await self._user_read_repository.get_by_email(email)
        if existing_user is not None:
            if exclude_user_id is None or existing_user.id_str != exclude_user_id:
                raise UserAlreadyExists(field_name="email", field_value=str(email))

    async def ensure_username_unique(
        self,
        username: Username,
        exclude_user_id: Optional[str] = None,
    ) -> None:
        """
        Ensure the username is unique across all users.
        Raises UserAlreadyExists if username is taken.
        """
        existing_user = await self._user_read_repository.get_by_username(username)
        if existing_user is not None:
            if exclude_user_id is None or existing_user.id_str != exclude_user_id:
                raise UserAlreadyExists(
                    field_name="username", field_value=str(username)
                )

    async def validate_new_user(
        self,
        email: Email,
        username: Username,
    ) -> None:
        """
        Validate a new user can be created with the given email and username.
        Raises appropriate exceptions if validation fails.
        """
        await self.ensure_email_unique(email)
        await self.ensure_username_unique(username)

    async def can_transfer_ownership(
        self,
        from_user: UserAggregate,
        to_user: UserAggregate,
    ) -> bool:
        """
        Check if ownership can be transferred from one user to another.
        Both users must be active and not deleted.
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
