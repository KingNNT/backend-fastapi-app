"""Standardized API response utilities.

This module provides consistent response formatting for all API endpoints,
ensuring uniform structure for both success and error responses.
"""

from typing import Any

from fastapi import status
from fastapi.responses import JSONResponse

from app.internal.exceptions.base import DomainException
from app.internal.exceptions.user import UserNotFound, UserAlreadyExists
from app.internal.exceptions.validation import ValidationError, BusinessRuleViolation


class APIResponse:
    """Utility class for creating standardized API responses."""

    @staticmethod
    def success_response(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: dict[str, Any] | None = None,
    ):
        """Create a standardized success response.

        Args:
            data: The response data/payload
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata (pagination, etc.)

        Returns:
            JSONResponse: Standardized success response
        """
        content = {"success": True, "message": message, "data": data}

        if meta:
            content["meta"] = meta

        return JSONResponse(status_code=status_code, content=content)

    @staticmethod
    def error_response(
        message: str,
        error_code: str | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        context: dict[str, Any] | None = None,
    ) -> JSONResponse:
        """Create a standardized error response.

        Args:
            message: Error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            context: Additional error context

        Returns:
            JSONResponse: Standardized error response
        """
        content = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": None,
        }

        if context:
            content["context"] = context

        return JSONResponse(status_code=status_code, content=content)

    @staticmethod
    def from_domain_exception(exc: DomainException) -> JSONResponse:
        """Create error response from domain exception.

        Args:
            exc: Domain exception instance

        Returns:
            JSONResponse: Standardized error response
        """
        # Determine status code based on exception type
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        context = None

        if isinstance(exc, UserNotFound):
            status_code = status.HTTP_404_NOT_FOUND
            context = {
                "user_id": exc.user_id,
                "email": exc.email,
                "username": exc.username,
            }
        elif isinstance(exc, UserAlreadyExists):
            status_code = status.HTTP_400_BAD_REQUEST
            context = {"field": exc.field, "value": exc.value}
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            context = {"field": exc.field, "value": exc.value}
        elif isinstance(exc, BusinessRuleViolation):
            status_code = status.HTTP_400_BAD_REQUEST
            context = {"rule": exc.rule, "context": exc.context}

        return APIResponse.error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=status_code,
            context=context,
        )
