"""Role-specific domain exceptions."""

from dataclasses import dataclass
from typing import Any, Optional

from app.shared.domain.base_exception import (
    EntityAlreadyExists,
    EntityNotFound,
)
from app.shared.domain.error_codes import ErrorCode


@dataclass
class RoleNotFound(EntityNotFound):
    """Exception raised when a role is not found."""

    entity_type: str = "Role"
    message: str = ""
    error_code: ErrorCode = ErrorCode.ROLE_NOT_FOUND

    def __init__(self, role_id: Optional[str] = None, message: str = ""):
        self.entity_id = role_id
        self.message = message or f"Role with id '{role_id}' not found"
        self.context: dict[str, Any] = {}
        super().__post_init__()


@dataclass
class RoleAlreadyExists(EntityAlreadyExists):
    """Exception raised when trying to create a role that already exists."""

    entity_type: str = "Role"
    message: str = ""
    error_code: ErrorCode = ErrorCode.ROLE_ALREADY_EXISTS

    def __init__(self, field_name: str = "name", field_value: Optional[str] = None):
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"Role with {field_name} '{field_value}' already exists"
        self.context: dict[str, Any] = {}
        super().__post_init__()
