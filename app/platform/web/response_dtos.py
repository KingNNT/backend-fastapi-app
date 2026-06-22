"""Generic response DTOs for the presentation layer."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from app.shared.domain.error_codes import ErrorCode

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response wrapper."""

    success: bool = Field(default=True, description="Whether the request succeeded")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    meta: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class ErrorResponse(BaseModel):
    """Generic error response wrapper."""

    success: bool = Field(default=False, description="Whether the request succeeded")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    data: None = Field(default=None, description="No data for errors")
    context: Optional[dict[str, Any]] = Field(None, description="Error context")


class CreatedResponse(SuccessResponse[T], Generic[T]):
    """Response for created resources (201)."""

    pass


class NotFoundResponse(ErrorResponse):
    """Response for not found resources (404)."""

    error_code: str = Field(default=ErrorCode.NOT_FOUND.value)


class ConflictResponse(ErrorResponse):
    """Response for conflict errors (409)."""

    error_code: str = Field(default=ErrorCode.CONFLICT.value)


class ValidationErrorResponse(ErrorResponse):
    """Response for validation errors (422)."""

    error_code: str = Field(default=ErrorCode.VALIDATION_ERROR.value)


class BadRequestResponse(ErrorResponse):
    """Response for bad request errors (400)."""

    error_code: str = Field(default=ErrorCode.BAD_REQUEST.value)
