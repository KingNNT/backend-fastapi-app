"""FastAPI exception handlers for domain exceptions."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.domain.exceptions import (
    InvalidUserState,
    UserAlreadyExists,
    UserNotFound,
)
from app.shared.domain import (
    BusinessRuleViolation,
    DomainException,
    EntityAlreadyExists,
    EntityNotFound,
    ErrorCode,
    ValidationError,
)


def create_error_response(
    message: str,
    error_code: str,
    status_code: int,
    context: dict | None = None,
) -> JSONResponse:
    """Create a standardized error response."""
    content = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "data": None,
    }
    if context:
        content["context"] = context
    return JSONResponse(status_code=status_code, content=content)


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    """Handle all domain exceptions."""
    # Determine status code and context based on exception type
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    context = exc.context if exc.context else None

    if isinstance(exc, UserNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, EntityNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, UserAlreadyExists):
        status_code = status.HTTP_409_CONFLICT
        context = {"field": exc.field_name, "value": exc.field_value}
    elif isinstance(exc, EntityAlreadyExists):
        status_code = status.HTTP_409_CONFLICT
        context = {"field": exc.field_name, "value": exc.field_value}
    elif isinstance(exc, InvalidUserState):
        status_code = status.HTTP_400_BAD_REQUEST
        context = {
            "current_state": exc.current_state,
            "required_state": exc.required_state,
        }
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        context = {
            "field": exc.field_name,
            "value": str(exc.field_value) if exc.field_value else None,
        }
    elif isinstance(exc, BusinessRuleViolation):
        status_code = status.HTTP_400_BAD_REQUEST
        context = {"rule": exc.rule_name}

    return create_error_response(
        message=exc.message,
        error_code=exc.error_code.value,
        status_code=status_code,
        context=context,
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions (often from value object validation)."""
    return create_error_response(
        message=str(exc),
        error_code=ErrorCode.VALIDATION_ERROR.value,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
