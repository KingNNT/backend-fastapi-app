"""Domain error codes - centralized enum for all domain errors."""

from enum import Enum


class ErrorCode(str, Enum):
    """
    Centralized error codes for domain exceptions.
    Inherits from str for JSON serialization compatibility.
    """

    # Base/generic errors
    DOMAIN_ERROR = "DOMAIN_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    BAD_REQUEST = "BAD_REQUEST"

    # Entity errors (generic)
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    ENTITY_ALREADY_EXISTS = "ENTITY_ALREADY_EXISTS"

    # User errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_USER_STATE = "INVALID_USER_STATE"

    # Log errors
    LOG_NOT_FOUND = "LOG_NOT_FOUND"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"

    # Authentication/Authorization errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
