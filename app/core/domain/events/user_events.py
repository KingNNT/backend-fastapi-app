"""User domain events."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from app.core.domain.events.base import BaseDomainEvent


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class UserCreated(BaseDomainEvent):
    """Event raised when a new user is created."""

    user_id: str = ""
    email: str = ""
    username: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
        }


@dataclass(frozen=True)
class UserUpdated(BaseDomainEvent):
    """Event raised when a user is updated."""

    user_id: str = ""
    changes: dict[str, Any] = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "changes": self.changes,
        }


@dataclass(frozen=True)
class UserDeleted(BaseDomainEvent):
    """Event raised when a user is deleted (soft delete)."""

    user_id: str = ""
    deleted_by: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "deleted_by": self.deleted_by,
        }


@dataclass(frozen=True)
class UserDeactivated(BaseDomainEvent):
    """Event raised when a user is deactivated."""

    user_id: str = ""
    reason: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class UserActivated(BaseDomainEvent):
    """Event raised when a user is activated."""

    user_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
        }


@dataclass(frozen=True)
class UserEmailUpdated(BaseDomainEvent):
    """Event raised when a user's email is updated."""

    user_id: str = ""
    old_email: str = ""
    new_email: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "old_email": self.old_email,
            "new_email": self.new_email,
        }


@dataclass(frozen=True)
class UserPasswordUpdated(BaseDomainEvent):
    """Event raised when a user's password is updated."""

    user_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
        }
