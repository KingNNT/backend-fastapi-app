"""Role domain events."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from app.core.domain.events.base import BaseDomainEvent


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class RoleCreated(BaseDomainEvent):
    """Event raised when a new role is created."""

    role_id: str = ""
    name: str = ""
    description: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "name": self.name,
            "description": self.description,
        }


@dataclass(frozen=True)
class RoleUpdated(BaseDomainEvent):
    """Event raised when a role is updated."""

    role_id: str = ""
    changes: dict[str, Any] = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "changes": self.changes,
        }


@dataclass(frozen=True)
class RoleDeleted(BaseDomainEvent):
    """Event raised when a role is deleted (soft delete)."""

    role_id: str = ""
    deleted_by: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "deleted_by": self.deleted_by,
        }


@dataclass(frozen=True)
class PermissionAssignedToRole(BaseDomainEvent):
    """Event raised when a permission is assigned to a role."""

    role_id: str = ""
    permission_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "permission_id": self.permission_id,
        }


@dataclass(frozen=True)
class PermissionRemovedFromRole(BaseDomainEvent):
    """Event raised when a permission is removed from a role."""

    role_id: str = ""
    permission_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "permission_id": self.permission_id,
        }


@dataclass(frozen=True)
class RoleAssignedToUser(BaseDomainEvent):
    """Event raised when a role is assigned to a user."""

    user_id: str = ""
    role_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role_id": self.role_id,
        }


@dataclass(frozen=True)
class RoleRemovedFromUser(BaseDomainEvent):
    """Event raised when a role is removed from a user."""

    user_id: str = ""
    role_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role_id": self.role_id,
        }
