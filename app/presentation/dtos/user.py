"""User DTOs for the presentation layer."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateRequest(BaseModel):
    """Request DTO for creating a user."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")


class UserUpdateRequest(BaseModel):
    """Request DTO for updating a user."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    password: Optional[str] = Field(None, min_length=8, description="User password")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")


class UserResponse(BaseModel):
    """Response DTO for user data."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User ID (UUID)")
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserListResponse(BaseModel):
    """Response DTO for user list with pagination."""

    data: list[UserResponse] = Field(..., description="List of users")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    count: int = Field(..., description="Items in current page")
    total: int = Field(..., description="Total items available")
