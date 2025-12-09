"""Standardized API response utilities."""

from typing import Any

from fastapi import status
from fastapi.responses import JSONResponse

from app.core.domain.exceptions.base import DomainException


class APIResponse:
    """Utility class for creating standardized API responses."""

    @staticmethod
    def success_response(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: dict[str, Any] | None = None,
    ) -> JSONResponse:
        """Create a standardized success response."""
        content: dict[str, Any] = {
            "success": True,
            "message": message,
            "data": data,
        }
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
        """Create a standardized error response."""
        content: dict[str, Any] = {
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
        """Create error response from domain exception."""
        return APIResponse.error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            context=exc.context if exc.context else None,
        )
