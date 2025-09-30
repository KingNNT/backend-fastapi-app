from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel, table=False):
    """Base model with audit trail and soft deletion for all entities."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the entity",
    )

    # Audit trail fields
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the entity was created"
    )
    created_by: Optional[str] = Field(
        default=None, description="Who created the entity"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="When the entity was last updated"
    )
    updated_by: Optional[str] = Field(
        default=None, description="Who last updated the entity"
    )

    # Soft deletion fields
    deleted_at: Optional[datetime] = Field(
        default=None, description="When the entity was soft deleted"
    )
    deleted_by: Optional[str] = Field(
        default=None, description="Who soft deleted the entity"
    )

    def soft_delete(self, deleted_by: Optional[str] = None) -> None:
        """Soft delete the entity."""
        self.deleted_at = datetime.now()
        self.deleted_by = deleted_by

    def is_deleted(self) -> bool:
        """Check if the entity is soft deleted."""
        return self.deleted_at is not None

    def update_audit(self, updated_by: Optional[str] = None) -> None:
        """Update audit fields."""
        self.updated_at = datetime.now()
        self.updated_by = updated_by
