"""Simple pagination response DTO for list APIs."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

# Type variable for list data types
T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    data: list[T] = Field(..., description="List of items")
    # Simple pagination metadata
    skip: int = Field(default=0, description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    count: int = Field(..., description="Number of items in current response")
    total: int = Field(..., description="Total number of items available")

    class Config:
        json_schema_extra = {}
