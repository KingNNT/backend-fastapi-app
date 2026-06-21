"""Permission domain events."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from app.shared.domain.base_event import BaseDomainEvent


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class PermissionCreated(BaseDomainEvent):
    """Event raised when a new permission is created."""

    permission_id: str = ""
    name: str = ""
    description: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "permission_id": self.permission_id,
            "name": self.name,
            "description": self.description,
        }


@dataclass(frozen=True)
class PermissionUpdated(BaseDomainEvent):
    """Event raised when a permission is updated."""

    permission_id: str = ""
    changes: dict[str, Any] = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "permission_id": self.permission_id,
            "changes": self.changes,
        }


@dataclass(frozen=True)
class PermissionDeleted(BaseDomainEvent):
    """Event raised when a permission is deleted (soft delete)."""

    permission_id: str = ""
    deleted_by: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "permission_id": self.permission_id,
            "deleted_by": self.deleted_by,
        }


@dataclass(frozen=True)
class PermissionAssignedToUser(BaseDomainEvent):
    """Event raised when a permission is directly assigned to a user."""

    user_id: str = ""
    permission_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "permission_id": self.permission_id,
        }


@dataclass(frozen=True)
class PermissionRemovedFromUser(BaseDomainEvent):
    """Event raised when a permission is removed from a user."""

    user_id: str = ""
    permission_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "permission_id": self.permission_id,
        }
