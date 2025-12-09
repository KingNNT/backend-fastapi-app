"""Log DTOs for the presentation layer."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class LogCreateRequest(BaseModel):
    """Request DTO for creating a log."""

    action: str = Field(..., description="Action type")
    user_id: Optional[str] = Field(None, description="User ID associated with the log")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Log metadata")


class LogResponse(BaseModel):
    """Response DTO for log data."""

    id: str = Field(..., description="Log ID")
    action: str = Field(..., description="Action type")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: datetime = Field(..., description="Log timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Log metadata")

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    """Response DTO for log list with pagination."""

    data: list[LogResponse] = Field(..., description="List of logs")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    count: int = Field(..., description="Items in current page")
    total: int = Field(..., description="Total items available")
