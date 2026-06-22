"""Permission model for PostgreSQL persistence."""

from typing import Optional

from sqlmodel import Field

from app.iam.infrastructure.persistence.postgresql.models.base import BaseModel


class PermissionModel(BaseModel, table=True):
    """Permission persistence model for PostgreSQL."""

    __tablename__ = "permissions"  # type: ignore

    name: str = Field(
        ...,
        unique=True,
        index=True,
        description="Permission name (e.g., users:read, roles:write)",
    )
    description: Optional[str] = Field(
        default=None,
        description="Permission description",
    )
