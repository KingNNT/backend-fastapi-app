"""User model for PostgreSQL persistence."""

from typing import Optional

from sqlmodel import Field

from app.iam.infrastructure.persistence.postgresql.models.base import BaseModel


class UserModel(BaseModel, table=True):
    """User persistence model for PostgreSQL (Write side)."""

    __tablename__ = "users"  # type: ignore

    email: str = Field(
        ...,
        unique=True,
        index=True,
        description="User email address",
    )
    username: str = Field(
        ...,
        unique=True,
        index=True,
        description="Username",
    )
    password: str = Field(
        ...,
        description="Hashed password",
    )
    full_name: Optional[str] = Field(
        default=None,
        description="Full name",
    )
    is_active: bool = Field(
        default=True,
        description="User active status",
    )
