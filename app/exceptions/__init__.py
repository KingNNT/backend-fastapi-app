"""Exception module for the application."""

from .base import DomainException
from .user import (
    UserAccountLocked,
    UserAlreadyExists,
    UserInactive,
    UserNotFound,
    UserPermissionDenied,
)
from .validation import BusinessRuleViolation, ValidationError

__all__ = [
    # Base exceptions
    "DomainException",
    # User exceptions
    "UserNotFound",
    "UserAlreadyExists",
    "UserInactive",
    "UserAccountLocked",
    "UserPermissionDenied",
    # Validation exceptions
    "ValidationError",
    "BusinessRuleViolation",
]
