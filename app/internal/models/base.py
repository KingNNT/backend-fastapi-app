from datetime import datetime, timezone
from uuid import UUID

from beanie import Document, PydanticObjectId
from pydantic import Field


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class BaseEntity(Document):
    id: PydanticObjectId | None = Field(default=None, description="Entity ID")
    created_at: datetime = Field(
        default_factory=utc_now, description="Creation timestamp"
    )
    created_by: UUID | None = Field(
        None, description="ID of user who created this entity"
    )
    updated_at: datetime = Field(
        default_factory=utc_now, description="Last update timestamp"
    )
    updated_by: UUID | None = Field(
        None, description="ID of user who last updated this entity"
    )
    deleted_at: datetime | None = Field(None, description="Soft deletion timestamp")
    deleted_by: UUID | None = Field(
        None, description="ID of user who deleted this entity"
    )

    class Settings:
        use_state_management = True

    @property
    def is_deleted(self) -> bool:
        """Check if entity is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self, deleted_by: UUID | None = None):
        """Mark entity as soft deleted."""
        now = utc_now()
        self.deleted_at = now
        self.deleted_by = deleted_by
        self.updated_at = now
        self.updated_by = deleted_by
