"""Base model for PostgreSQL persistence."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Get current UTC time (timezone-naive for database compatibility)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BaseModel(SQLModel, table=False):
    """Base model with audit trail and soft deletion for PostgreSQL entities."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the entity",
    )

    # Audit trail fields
    created_at: datetime = Field(
        default_factory=utc_now,
        description="When the entity was created",
    )
    created_by: Optional[UUID] = Field(
        default=None,
        description="Who created the entity",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        description="When the entity was last updated",
    )
    updated_by: Optional[UUID] = Field(
        default=None,
        description="Who last updated the entity",
    )

    # Soft deletion fields
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="When the entity was soft deleted",
    )
    deleted_by: Optional[UUID] = Field(
        default=None,
        description="Who soft deleted the entity",
    )

    def soft_delete(self, deleted_by: Optional[UUID] = None) -> None:
        """Soft delete the entity."""
        self.deleted_at = utc_now()
        self.deleted_by = deleted_by

    def is_deleted(self) -> bool:
        """Check if the entity is soft deleted."""
        return self.deleted_at is not None

    def update_audit(self, updated_by: Optional[UUID] = None) -> None:
        """Update audit fields."""
        self.updated_at = utc_now()
        self.updated_by = updated_by
