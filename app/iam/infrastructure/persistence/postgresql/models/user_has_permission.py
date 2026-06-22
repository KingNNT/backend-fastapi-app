"""User-Permission junction model for PostgreSQL persistence."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, UniqueConstraint


def utc_now() -> datetime:
    """Get current UTC time (timezone-naive for database compatibility)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class UserHasPermissionModel(SQLModel, table=True):
    """Junction table for user-permission many-to-many relationship."""

    __tablename__ = "user_has_permission"  # type: ignore
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_has_permission"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the assignment",
    )
    user_id: UUID = Field(
        ...,
        foreign_key="users.id",
        index=True,
        description="Reference to user",
    )
    permission_id: UUID = Field(
        ...,
        foreign_key="permissions.id",
        index=True,
        description="Reference to permission",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="When the permission was assigned",
    )
