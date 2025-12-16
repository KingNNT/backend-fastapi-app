"""Permission-specific domain exceptions."""

from dataclasses import dataclass
from typing import Any, Optional

from app.core.domain.exceptions.base import (
    EntityAlreadyExists,
    EntityNotFound,
)
from app.core.domain.exceptions.error_codes import ErrorCode


@dataclass
class PermissionNotFound(EntityNotFound):
    """Exception raised when a permission is not found."""

    entity_type: str = "Permission"
    message: str = ""
    error_code: ErrorCode = ErrorCode.PERMISSION_NOT_FOUND

    def __init__(self, permission_id: Optional[str] = None, message: str = ""):
        self.entity_id = permission_id
        self.message = message or f"Permission with id '{permission_id}' not found"
        self.context: dict[str, Any] = {}
        super().__post_init__()


@dataclass
class PermissionAlreadyExists(EntityAlreadyExists):
    """Exception raised when trying to create a permission that already exists."""

    entity_type: str = "Permission"
    message: str = ""
    error_code: ErrorCode = ErrorCode.PERMISSION_ALREADY_EXISTS

    def __init__(self, field_name: str = "name", field_value: Optional[str] = None):
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"Permission with {field_name} '{field_value}' already exists"
        self.context: dict[str, Any] = {}
        super().__post_init__()
