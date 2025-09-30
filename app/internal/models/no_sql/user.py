from pydantic import Field, EmailStr

from .base import BaseEntity


class User(BaseEntity):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., description="Hashed password")
    full_name: str | None = Field(None, max_length=255, description="Full name")
    is_active: bool = Field(default=True, description="User active status")

    class Settings(BaseEntity.Settings):
        name = "users"
        indexes = [
            "email",
            "username",
            [("email", 1), ("deleted_at", 1)],
            [("username", 1), ("deleted_at", 1)],
        ]
