"""Base exception classes for the application."""


class DomainException(Exception):
    """Base exception for domain-related errors.

    All domain exceptions should inherit from this class to enable
    consistent error handling across the application.
    """

    def __init__(self, message: str, error_code: str | None = None):
        """Initialize domain exception.

        Args:
            message: Human-readable error message
            error_code: Optional machine-readable error code
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ApplicationException(DomainException):
    """Base exception for application-level errors.

    These are typically system-level errors that are not directly
    related to business domain logic.
    """

    pass


class InfrastructureException(DomainException):
    """Base exception for infrastructure-related errors.

    These include database connection errors, external service failures,
    file system errors, etc.
    """

    pass
