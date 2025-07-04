"""Examples of how to use the exception system.

This file demonstrates proper usage of domain exceptions
throughout the application layers.
"""

from app.exceptions import (
    BusinessRuleViolation,
    UserAccountLocked,
    UserAlreadyExists,
    UserInactive,
    UserNotFound,
    UserPermissionDenied,
    ValidationError,
)
from app.exceptions.infrastructure import (
    DatabaseConnectionError,
    ExternalServiceUnavailable,
    FileNotFoundError,
)


def service_layer_examples():
    """Examples of raising exceptions in the service layer."""

    # User not found examples
    raise UserNotFound(user_id="123e4567-e89b-12d3-a456-426614174000")
    raise UserNotFound(email="user@example.com")
    raise UserNotFound(username="johndoe")

    # User already exists examples
    raise UserAlreadyExists("email", "user@example.com")
    raise UserAlreadyExists("username", "johndoe")

    # Business rule violations
    raise BusinessRuleViolation(
        rule="max_login_attempts",
        message="User has exceeded maximum login attempts",
        context={"attempts": 5, "max_allowed": 3},
    )

    # User state exceptions
    raise UserInactive("123e4567-e89b-12d3-a456-426614174000")
    raise UserAccountLocked(
        "123e4567-e89b-12d3-a456-426614174000", reason="Suspicious activity detected"
    )
    raise UserPermissionDenied(
        "123e4567-e89b-12d3-a456-426614174000", "delete_other_users"
    )

    # Validation errors
    raise ValidationError(
        field="password",
        message="Password must contain at least one uppercase letter",
        value="weakpassword",
    )


def infrastructure_layer_examples():
    """Examples of raising infrastructure exceptions."""

    # Database exceptions
    raise DatabaseConnectionError("Connection timeout after 30 seconds")

    # External service exceptions
    raise ExternalServiceUnavailable("payment_gateway", status_code=503)

    # File system exceptions
    raise FileNotFoundError("/path/to/config.json")


def exception_handling_patterns():
    """Examples of handling exceptions in different layers."""

    # Service layer - catching and re-raising with context
    try:
        # Some operation that might fail
        pass
    except UserNotFound as e:
        # Add more context and re-raise
        raise BusinessRuleViolation(
            rule="user_existence_required",
            message=f"Operation requires existing user: {e.message}",
            context={"original_error": e.error_code},
        )

    # Repository layer - converting infrastructure errors to domain errors
    try:
        # Database operation
        pass
    except DatabaseConnectionError as e:
        raise BusinessRuleViolation(
            rule="data_availability",
            message="Unable to access user data",
            context={"infrastructure_error": str(e)},
        )


def http_response_examples():
    """Examples of how exceptions translate to HTTP responses."""

    # UserNotFound -> 404 Not Found
    # {
    #     "detail": "User with ID '123' not found",
    #     "error_code": "USER_NOT_FOUND_BY_ID",
    #     "context": {
    #         "user_id": "123",
    #         "email": null,
    #         "username": null
    #     }
    # }

    # UserAlreadyExists -> 400 Bad Request
    # {
    #     "detail": "User with email 'user@example.com' already exists",
    #     "error_code": "USER_ALREADY_EXISTS_BY_EMAIL",
    #     "context": {
    #         "field": "email",
    #         "value": "user@example.com"
    #     }
    # }

    # ValidationError -> 422 Unprocessable Entity
    # {
    #     "detail": "Validation error for 'password': Password too weak",
    #     "error_code": "VALIDATION_ERROR",
    #     "context": {
    #         "field": "password",
    #         "value": "weak"
    #     }
    # }

    # BusinessRuleViolation -> 400 Bad Request
    # {
    #     "detail": "Business rule violation 'max_login_attempts': Too many failed attempts",
    #     "error_code": "BUSINESS_RULE_VIOLATION_MAX_LOGIN_ATTEMPTS",
    #     "context": {
    #         "rule": "max_login_attempts",
    #         "context": {"attempts": 5, "max_allowed": 3}
    #     }
    # }
    pass
