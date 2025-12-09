"""User aggregate - consistency boundary for user operations."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from app.core.domain.entities.user import User
from app.core.domain.events.base import BaseDomainEvent
from app.core.domain.events.user_events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserEmailUpdated,
    UserPasswordUpdated,
    UserUpdated,
)
from app.core.domain.exceptions.user import InvalidUserState
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.user_id import UserId
from app.core.domain.value_objects.username import Username


@dataclass
class UserAggregate:
    """
    User aggregate root - ensures consistency for user operations.
    All modifications to user data must go through this aggregate.
    """

    _user: User
    _events: list[BaseDomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        email: Email,
        username: Username,
        password_hash: str,
        full_name: Optional[str] = None,
    ) -> "UserAggregate":
        """Factory method to create a new user aggregate."""
        user = User(
            id=UserId.generate(),
            email=email,
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            is_active=True,
        )
        aggregate = cls(_user=user)
        aggregate._events.append(
            UserCreated(
                user_id=user.id_str,
                email=user.email_str,
                username=user.username_str,
            )
        )
        return aggregate

    @classmethod
    def reconstitute(cls, user: User) -> "UserAggregate":
        """Reconstitute aggregate from existing user entity (from repository)."""
        return cls(_user=user)

    @property
    def user(self) -> User:
        """Get the underlying user entity."""
        return self._user

    @property
    def id(self) -> UserId:
        """Get user ID."""
        return self._user.id

    @property
    def id_str(self) -> str:
        """Get user ID as string."""
        return self._user.id_str

    @property
    def events(self) -> list[BaseDomainEvent]:
        """Get domain events raised by this aggregate."""
        return self._events.copy()

    def clear_events(self) -> None:
        """Clear domain events after they've been dispatched."""
        self._events.clear()

    def update_email(self, new_email: Email) -> None:
        """Update user's email."""
        if not self._user.is_active:
            raise InvalidUserState(
                message="Cannot update email of inactive user",
                current_state="inactive",
                required_state="active",
            )
        old_email = self._user.email_str
        self._user.update_email(new_email)
        self._events.append(
            UserEmailUpdated(
                user_id=self._user.id_str,
                old_email=old_email,
                new_email=str(new_email),
            )
        )

    def update_password(self, new_password_hash: str) -> None:
        """Update user's password."""
        if not self._user.is_active:
            raise InvalidUserState(
                message="Cannot update password of inactive user",
                current_state="inactive",
                required_state="active",
            )
        self._user.update_password(new_password_hash)
        self._events.append(UserPasswordUpdated(user_id=self._user.id_str))

    def update_profile(
        self,
        full_name: Optional[str] = None,
        username: Optional[Username] = None,
    ) -> None:
        """Update user's profile information."""
        if not self._user.is_active:
            raise InvalidUserState(
                message="Cannot update profile of inactive user",
                current_state="inactive",
                required_state="active",
            )
        changes: dict = {}
        if full_name is not None:
            changes["full_name"] = full_name
        if username is not None:
            changes["username"] = str(username)

        self._user.update_profile(full_name=full_name, username=username)

        if changes:
            self._events.append(UserUpdated(user_id=self._user.id_str, changes=changes))

    def deactivate(self, reason: Optional[str] = None) -> None:
        """Deactivate the user."""
        if not self._user.is_active:
            raise InvalidUserState(
                message="User is already inactive",
                current_state="inactive",
                required_state="active",
            )
        self._user.deactivate()
        self._events.append(UserDeactivated(user_id=self._user.id_str, reason=reason))

    def activate(self) -> None:
        """Activate the user."""
        if self._user.is_active:
            raise InvalidUserState(
                message="User is already active",
                current_state="active",
                required_state="inactive",
            )
        self._user.activate()
        self._events.append(UserActivated(user_id=self._user.id_str))

    def soft_delete(self, deleted_by: Optional[UUID] = None) -> None:
        """Soft delete the user."""
        self._user.soft_delete(deleted_by=deleted_by)
        self._events.append(
            UserDeleted(
                user_id=self._user.id_str,
                deleted_by=str(deleted_by) if deleted_by else None,
            )
        )
