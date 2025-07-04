from datetime import datetime
from uuid import UUID

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str | None = Field(None, max_length=255, description="Full name")
    is_active: bool = Field(default=True, description="User active status")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: PydanticObjectId = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: UUID | None = Field(
        None, description="ID of user who created this user"
    )
    updated_at: datetime = Field(..., description="Last update timestamp")
    updated_by: UUID | None = Field(
        None, description="ID of user who last updated this user"
    )

    class Config:
        from_attributes = True
