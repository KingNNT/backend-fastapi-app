# Base exceptions
from .base import ApplicationException, DomainException, InfrastructureException

# Handlers
from .handlers import (
    BaseExceptionHandler,
    BusinessRuleViolationHandler,
    DomainExceptionHandler,
    HttpExceptionConverter,
    UserAlreadyExistsHandler,
    UserNotFoundHandler,
    ValidationErrorHandler,
    register_exception_handlers,
)

# Infrastructure exceptions
from .infrastructure import (
    DatabaseConnectionError,
    DatabaseException,
    DatabaseTimeoutError,
    ExternalServiceException,
    ExternalServiceTimeout,
    ExternalServiceUnavailable,
    FileNotFoundError,
    FilePermissionError,
    FileSystemException,
)

# User exceptions
from .user import (
    UserAccountLocked,
    UserAlreadyExists,
    UserException,
    UserInactive,
    UserNotFound,
    UserPermissionDenied,
)

# Validation exceptions
from .validation import (
    BusinessRuleViolation,
    ConcurrencyError,
    DataIntegrityError,
    InvalidOperationError,
    ValidationError,
    ValidationException,
)

__all__ = [
    # Base
    "DomainException",
    "ApplicationException",
    "InfrastructureException",
    # Handlers
    "BaseExceptionHandler",
    "DomainExceptionHandler",
    "UserNotFoundHandler",
    "UserAlreadyExistsHandler",
    "ValidationErrorHandler",
    "BusinessRuleViolationHandler",
    "HttpExceptionConverter",
    "register_exception_handlers",
    # Infrastructure
    "DatabaseException",
    "DatabaseConnectionError",
    "DatabaseTimeoutError",
    "ExternalServiceException",
    "ExternalServiceUnavailable",
    "ExternalServiceTimeout",
    "FileSystemException",
    "FileNotFoundError",
    "FilePermissionError",
    # User
    "UserException",
    "UserNotFound",
    "UserAlreadyExists",
    "UserInactive",
    "UserPermissionDenied",
    "UserAccountLocked",
    # Validation
    "ValidationException",
    "ValidationError",
    "BusinessRuleViolation",
    "InvalidOperationError",
    "DataIntegrityError",
    "ConcurrencyError",
]
