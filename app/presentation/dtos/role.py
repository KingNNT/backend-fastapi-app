"""Role DTOs for the presentation layer."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleCreateRequest(BaseModel):
    """Request DTO for creating a role."""

    name: str = Field(..., min_length=2, max_length=100, description="Role name")
    description: Optional[str] = Field(
        None, max_length=500, description="Role description"
    )


class RoleUpdateRequest(BaseModel):
    """Request DTO for updating a role."""

    name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Role name"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Role description"
    )


class RoleResponse(BaseModel):
    """Response DTO for role data."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Role ID (UUID)")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class RoleListResponse(BaseModel):
    """Response DTO for role list with pagination."""

    data: list[RoleResponse] = Field(..., description="List of roles")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    count: int = Field(..., description="Items in current page")
    total: int = Field(..., description="Total items available")


class AssignPermissionRequest(BaseModel):
    """Request DTO for assigning a permission to a role."""

    permission_id: str = Field(..., description="Permission ID to assign")
