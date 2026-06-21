"""Role model for PostgreSQL persistence."""

from typing import Optional

from sqlmodel import Field

from app.iam.infrastructure.persistence.postgresql.models.base import BaseModel


class RoleModel(BaseModel, table=True):
    """Role persistence model for PostgreSQL."""

    __tablename__ = "roles"  # type: ignore

    name: str = Field(
        ...,
        unique=True,
        index=True,
        description="Role name",
    )
    description: Optional[str] = Field(
        default=None,
        description="Role description",
    )
