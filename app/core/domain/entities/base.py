"""Base entity with common audit fields."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


@dataclass
class BaseEntity:
    """
    Base entity with audit trail and soft deletion support.
    All entities should inherit from this class.
    """

    created_at: datetime = field(default_factory=utc_now)
    created_by: Optional[UUID] = None
    updated_at: datetime = field(default_factory=utc_now)
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None

    @property
    def is_deleted(self) -> bool:
        """Check if entity is soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self, deleted_by: Optional[UUID] = None) -> None:
        """Mark entity as soft-deleted."""
        now = utc_now()
        # Use object.__setattr__ for frozen dataclasses if needed
        self.deleted_at = now
        self.deleted_by = deleted_by
        self.updated_at = now
        self.updated_by = deleted_by

    def mark_updated(self, updated_by: Optional[UUID] = None) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = utc_now()
        self.updated_by = updated_by
