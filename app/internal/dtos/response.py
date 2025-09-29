"""Standardized response DTOs for OpenAPI documentation.

This module provides Pydantic models that match the APIResponse utility format,
ensuring consistent OpenAPI documentation generation.
"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# Type variable for generic data types
T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model with common fields."""

    success: bool = Field(..., description="Indicates if the operation was successful")
    message: str = Field(
        ..., description="Human-readable message describing the result"
    )


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success response model.

    This matches the format returned by APIResponse.success_response().
    """

    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Message of response")
    data: T = Field(..., description="The response payload/data")

    class Config:
        json_schema_extra = {}


class ErrorResponse(BaseResponse):
    """Standardized error response model.

    This matches the format returned by APIResponse.error_response().
    """

    success: bool = Field(False, description="Always false for error responses")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    data: None = Field(None, description="Always null for error responses")
    context: Optional[dict[str, Any]] = Field(
        None, description="Additional error context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "data": None,
                "context": {"field": "email", "value": "invalid-email"},
            }
        }


class EmptySuccessResponse(BaseResponse):
    """Success response without data (for 204 responses)."""

    success: bool = Field(True, description="Always true for success responses")

    class Config:
        json_schema_extra = {
            "example": {"success": True, "message": "Operation completed successfully"}
        }


# Common response types for different HTTP status codes
class CreatedResponse(SuccessResponse[T], Generic[T]):
    """Success response for 201 Created operations."""

    class Config:
        json_schema_extra = {}


class NotFoundResponse(ErrorResponse):
    """Error response for 404 Not Found."""

    class Config:
        json_schema_extra = {}


class ValidationErrorResponse(ErrorResponse):
    """Error response for 422 Validation Error."""

    class Config:
        json_schema_extra = {}


class ConflictResponse(ErrorResponse):
    """Error response for 409 Conflict."""

    class Config:
        json_schema_extra = {}


class BadRequestResponse(ErrorResponse):
    """Error response for 400 Bad Request."""

    class Config:
        json_schema_extra = {}
