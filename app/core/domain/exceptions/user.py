"""User-specific domain exceptions."""

from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.domain.exceptions.base import (
    DomainException,
    EntityAlreadyExists,
    EntityNotFound,
)
from app.core.domain.exceptions.error_codes import ErrorCode


@dataclass
class UserNotFound(EntityNotFound):
    """Exception raised when a user is not found."""

    entity_type: str = "User"
    message: str = ""
    error_code: ErrorCode = ErrorCode.USER_NOT_FOUND

    def __init__(self, user_id: Optional[str] = None, message: str = ""):
        self.entity_id = user_id
        self.message = message or f"User with id '{user_id}' not found"
        self.context: dict[str, Any] = {}
        super().__post_init__()


@dataclass
class UserAlreadyExists(EntityAlreadyExists):
    """Exception raised when trying to create a user that already exists."""

    entity_type: str = "User"
    message: str = ""
    error_code: ErrorCode = ErrorCode.USER_ALREADY_EXISTS

    def __init__(self, field_name: str = "email", field_value: Optional[str] = None):
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"User with {field_name} '{field_value}' already exists"
        self.context: dict[str, Any] = {}
        super().__post_init__()


@dataclass
class InvalidUserState(DomainException):
    """Exception raised when an operation is invalid for the current user state."""

    message: str = "Invalid user state for this operation"
    error_code: ErrorCode = ErrorCode.INVALID_USER_STATE
    current_state: Optional[str] = None
    required_state: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.current_state and self.required_state:
            self.context = {
                "current_state": self.current_state,
                "required_state": self.required_state,
            }
        super().__post_init__()
