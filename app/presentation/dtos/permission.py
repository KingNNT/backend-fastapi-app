"""Permission DTOs for the presentation layer."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PermissionCreateRequest(BaseModel):
    """Request DTO for creating a permission."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Permission name (e.g., users:read, roles:write)",
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Permission description"
    )


class PermissionUpdateRequest(BaseModel):
    """Request DTO for updating a permission."""

    name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Permission name"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Permission description"
    )


class PermissionResponse(BaseModel):
    """Response DTO for permission data."""

    id: str = Field(..., description="Permission ID (UUID)")
    name: str = Field(..., description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    """Response DTO for permission list with pagination."""

    data: list[PermissionResponse] = Field(..., description="List of permissions")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    count: int = Field(..., description="Items in current page")
    total: int = Field(..., description="Total items available")
