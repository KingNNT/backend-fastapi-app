"""Role-Permission junction model for PostgreSQL persistence."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, UniqueConstraint


def utc_now() -> datetime:
    """Get current UTC time (timezone-naive for database compatibility)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RoleHasPermissionsModel(SQLModel, table=True):
    """Junction table for role-permission many-to-many relationship."""

    __tablename__ = "role_has_permissions"  # type: ignore
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_has_permissions"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the assignment",
    )
    role_id: UUID = Field(
        ...,
        foreign_key="roles.id",
        index=True,
        description="Reference to role",
    )
    permission_id: UUID = Field(
        ...,
        foreign_key="permissions.id",
        index=True,
        description="Reference to permission",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="When the permission was assigned to the role",
    )
