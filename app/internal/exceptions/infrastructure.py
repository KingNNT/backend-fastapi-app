"""Infrastructure-related exceptions."""

from .base import InfrastructureException


class DatabaseException(InfrastructureException):
    """Base exception for database-related errors."""

    pass


class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails."""

    def __init__(self, details: str | None = None):
        """Initialize DatabaseConnectionError exception.

        Args:
            details: Optional connection error details
        """
        message = "Database connection failed"
        if details:
            message += f": {details}"
        error_code = "DATABASE_CONNECTION_ERROR"

        self.details = details
        super().__init__(message, error_code)


class DatabaseTimeoutError(DatabaseException):
    """Raised when database operation times out."""

    def __init__(self, operation: str, timeout_seconds: float):
        """Initialize DatabaseTimeoutError exception.

        Args:
            operation: The operation that timed out
            timeout_seconds: Timeout duration in seconds
        """
        message = f"Database operation '{operation}' timed out after {timeout_seconds} seconds"
        error_code = "DATABASE_TIMEOUT_ERROR"

        self.operation = operation
        self.timeout_seconds = timeout_seconds
        super().__init__(message, error_code)


class ExternalServiceException(InfrastructureException):
    """Base exception for external service errors."""

    pass


class ExternalServiceUnavailable(ExternalServiceException):
    """Raised when external service is unavailable."""

    def __init__(self, service_name: str, status_code: int | None = None):
        """Initialize ExternalServiceUnavailable exception.

        Args:
            service_name: Name of the unavailable service
            status_code: Optional HTTP status code
        """
        message = f"External service '{service_name}' is unavailable"
        if status_code:
            message += f" (status: {status_code})"
        error_code = "EXTERNAL_SERVICE_UNAVAILABLE"

        self.service_name = service_name
        self.status_code = status_code
        super().__init__(message, error_code)


class ExternalServiceTimeout(ExternalServiceException):
    """Raised when external service call times out."""

    def __init__(self, service_name: str, timeout_seconds: float):
        """Initialize ExternalServiceTimeout exception.

        Args:
            service_name: Name of the service
            timeout_seconds: Timeout duration in seconds
        """
        message = f"External service '{service_name}' timed out after {timeout_seconds} seconds"
        error_code = "EXTERNAL_SERVICE_TIMEOUT"

        self.service_name = service_name
        self.timeout_seconds = timeout_seconds
        super().__init__(message, error_code)


class FileSystemException(InfrastructureException):
    """Base exception for file system errors."""

    pass


class FileNotFoundError(FileSystemException):
    """Raised when a required file is not found."""

    def __init__(self, file_path: str):
        """Initialize FileNotFoundError exception.

        Args:
            file_path: Path to the file that was not found
        """
        message = f"File not found: {file_path}"
        error_code = "FILE_NOT_FOUND"

        self.file_path = file_path
        super().__init__(message, error_code)


class FilePermissionError(FileSystemException):
    """Raised when file operation is denied due to permissions."""

    def __init__(self, file_path: str, operation: str):
        """Initialize FilePermissionError exception.

        Args:
            file_path: Path to the file
            operation: The operation that was denied
        """
        message = f"Permission denied for {operation} operation on file: {file_path}"
        error_code = "FILE_PERMISSION_ERROR"

        self.file_path = file_path
        self.operation = operation
        super().__init__(message, error_code)
