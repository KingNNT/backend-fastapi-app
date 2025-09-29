"""Exception handlers for converting domain exceptions to HTTP responses."""

from abc import ABC, abstractmethod

from .base import DomainException
from .user import UserNotFound, UserAlreadyExists
from .validation import ValidationError, BusinessRuleViolation
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.utils.response import APIResponse


class BaseExceptionHandler(ABC):
    """Base class for exception handlers."""

    @abstractmethod
    async def handle(self, request: Request, exc: DomainException) -> JSONResponse:
        """Handle the exception and return JSON response."""
        pass


class DomainExceptionHandler(BaseExceptionHandler):
    """Generic handler for domain exceptions."""

    async def handle(self, request: Request, exc: DomainException) -> JSONResponse:
        return APIResponse.from_domain_exception(exc)


class UserNotFoundHandler(BaseExceptionHandler):
    """Handler for UserNotFound exceptions."""

    async def handle(self, request: Request, exc: UserNotFound) -> JSONResponse:
        return APIResponse.from_domain_exception(exc)


class UserAlreadyExistsHandler(BaseExceptionHandler):
    """Handler for UserAlreadyExists exceptions."""

    async def handle(self, request: Request, exc: UserAlreadyExists) -> JSONResponse:
        return APIResponse.from_domain_exception(exc)


class ValidationErrorHandler(BaseExceptionHandler):
    """Handler for ValidationError exceptions."""

    async def handle(self, request: Request, exc: ValidationError) -> JSONResponse:
        return APIResponse.from_domain_exception(exc)


class BusinessRuleViolationHandler(BaseExceptionHandler):
    """Handler for BusinessRuleViolation exceptions."""

    async def handle(
        self, request: Request, exc: BusinessRuleViolation
    ) -> JSONResponse:
        return APIResponse.from_domain_exception(exc)


# Handler instances
domain_exception_handler = DomainExceptionHandler()
user_not_found_handler = UserNotFoundHandler()
user_already_exists_handler = UserAlreadyExistsHandler()
validation_error_handler = ValidationErrorHandler()
business_rule_violation_handler = BusinessRuleViolationHandler()


def register_exception_handlers(app) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(UserNotFound, user_not_found_handler.handle)
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler.handle)
    app.add_exception_handler(ValidationError, validation_error_handler.handle)
    app.add_exception_handler(
        BusinessRuleViolation, business_rule_violation_handler.handle
    )
    app.add_exception_handler(DomainException, domain_exception_handler.handle)


class HttpExceptionConverter:
    """Convert domain exceptions to HTTP exceptions (alternative approach)."""

    @staticmethod
    def convert(exc: DomainException) -> None:
        """Convert domain exception to HTTP exception."""
        if isinstance(exc, UserNotFound):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
            )
        elif isinstance(exc, UserAlreadyExists):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message
            )
        elif isinstance(exc, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
            )
        elif isinstance(exc, BusinessRuleViolation):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.message
            )
