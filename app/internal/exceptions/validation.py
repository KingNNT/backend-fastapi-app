"""Validation and business rule exceptions."""

from .base import DomainException


class ValidationException(DomainException):
    """Base exception for validation-related errors."""

    pass


class ValidationError(ValidationException):
    """Raised when domain validation fails."""

    def __init__(self, field: str, message: str, value: str | None = None):
        """Initialize ValidationError exception.

        Args:
            field: The field that failed validation
            message: Validation error message
            value: The invalid value (optional)
        """
        full_message = f"Validation error for '{field}': {message}"
        error_code = "VALIDATION_ERROR"

        self.field = field
        self.validation_message = message
        self.value = value
        super().__init__(full_message, error_code)


class BusinessRuleViolation(DomainException):
    """Raised when a business rule is violated."""

    def __init__(self, rule: str, message: str, context: dict | None = None):
        """Initialize BusinessRuleViolation exception.

        Args:
            rule: The business rule that was violated
            message: Description of the violation
            context: Optional context information
        """
        full_message = f"Business rule violation '{rule}': {message}"
        error_code = f"BUSINESS_RULE_VIOLATION_{rule.upper()}"

        self.rule = rule
        self.rule_message = message
        self.context = context or {}
        super().__init__(full_message, error_code)


class InvalidOperationError(ValidationException):
    """Raised when an operation is invalid in the current context."""

    def __init__(self, operation: str, reason: str, current_state: str | None = None):
        """Initialize InvalidOperationError exception.

        Args:
            operation: The operation that is invalid
            reason: Why the operation is invalid
            current_state: Optional current state description
        """
        message = f"Invalid operation '{operation}': {reason}"
        if current_state:
            message += f" (current state: {current_state})"
        error_code = "INVALID_OPERATION"

        self.operation = operation
        self.reason = reason
        self.current_state = current_state
        super().__init__(message, error_code)


class DataIntegrityError(ValidationException):
    """Raised when data integrity constraints are violated."""

    def __init__(self, constraint: str, details: str | None = None):
        """Initialize DataIntegrityError exception.

        Args:
            constraint: The integrity constraint that was violated
            details: Optional additional details
        """
        message = f"Data integrity constraint violated: {constraint}"
        if details:
            message += f" - {details}"
        error_code = "DATA_INTEGRITY_ERROR"

        self.constraint = constraint
        self.details = details
        super().__init__(message, error_code)


class ConcurrencyError(ValidationException):
    """Raised when concurrent modification conflicts occur."""

    def __init__(self, resource_type: str, resource_id: str):
        """Initialize ConcurrencyError exception.

        Args:
            resource_type: Type of resource that had conflict
            resource_id: ID of the resource
        """
        message = f"Concurrency conflict on {resource_type} '{resource_id}'"
        error_code = "CONCURRENCY_ERROR"

        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message, error_code)
