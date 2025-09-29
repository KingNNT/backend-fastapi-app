"""User domain exceptions."""

from .base import DomainException


class UserException(DomainException):
    """Base exception for user-related errors."""

    pass


class UserNotFound(UserException):
    """Raised when a user cannot be found."""

    def __init__(
        self,
        user_id: str | None = None,
        email: str | None = None,
        username: str | None = None,
    ):
        """Initialize UserNotFound exception.

        Args:
            user_id: User ID that was not found
            email: Email that was not found
            username: Username that was not found
        """
        if user_id:
            message = f"User with ID '{user_id}' not found"
            error_code = "USER_NOT_FOUND_BY_ID"
        elif email:
            message = f"User with email '{email}' not found"
            error_code = "USER_NOT_FOUND_BY_EMAIL"
        elif username:
            message = f"User with username '{username}' not found"
            error_code = "USER_NOT_FOUND_BY_USERNAME"
        else:
            message = "User not found"
            error_code = "USER_NOT_FOUND"

        self.user_id = user_id
        self.email = email
        self.username = username
        super().__init__(message, error_code)


class UserAlreadyExists(UserException):
    """Raised when trying to create a user that already exists."""

    def __init__(self, field: str, value: str):
        """Initialize UserAlreadyExists exception.

        Args:
            field: The field that already exists (e.g., 'email', 'username')
            value: The value that already exists
        """
        message = f"User with {field} '{value}' already exists"
        error_code = f"USER_ALREADY_EXISTS_BY_{field.upper()}"

        self.field = field
        self.value = value
        super().__init__(message, error_code)


class UserInactive(UserException):
    """Raised when attempting operations on an inactive user."""

    def __init__(self, user_id: str):
        """Initialize UserInactive exception.

        Args:
            user_id: ID of the inactive user
        """
        message = f"User '{user_id}' is inactive"
        error_code = "USER_INACTIVE"

        self.user_id = user_id
        super().__init__(message, error_code)


class UserPermissionDenied(UserException):
    """Raised when user doesn't have permission for an operation."""

    def __init__(self, user_id: str, operation: str):
        """Initialize UserPermissionDenied exception.

        Args:
            user_id: ID of the user
            operation: The operation that was denied
        """
        message = (
            f"User '{user_id}' does not have permission for operation '{operation}'"
        )
        error_code = "USER_PERMISSION_DENIED"

        self.user_id = user_id
        self.operation = operation
        super().__init__(message, error_code)


class UserAccountLocked(UserException):
    """Raised when user account is locked."""

    def __init__(self, user_id: str, reason: str | None = None):
        """Initialize UserAccountLocked exception.

        Args:
            user_id: ID of the locked user
            reason: Optional reason for the lock
        """
        message = f"User account '{user_id}' is locked"
        if reason:
            message += f": {reason}"
        error_code = "USER_ACCOUNT_LOCKED"

        self.user_id = user_id
        self.reason = reason
        super().__init__(message, error_code)
