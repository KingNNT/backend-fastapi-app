"""Domain exceptions - business logic errors."""

from app.core.domain.exceptions.base import (
    DomainException,
    EntityAlreadyExists,
    EntityNotFound,
)
from app.core.domain.exceptions.error_codes import ErrorCode
from app.core.domain.exceptions.permission import (
    PermissionAlreadyExists,
    PermissionNotFound,
)
from app.core.domain.exceptions.role import (
    RoleAlreadyExists,
    RoleNotFound,
)
from app.core.domain.exceptions.user import (
    InvalidUserState,
    UserAlreadyExists,
    UserNotFound,
)
from app.core.domain.exceptions.validation import (
    BusinessRuleViolation,
    ValidationError,
)

__all__ = [
    "ErrorCode",
    "DomainException",
    "EntityNotFound",
    "EntityAlreadyExists",
    "UserNotFound",
    "UserAlreadyExists",
    "InvalidUserState",
    "ValidationError",
    "BusinessRuleViolation",
    "RoleNotFound",
    "RoleAlreadyExists",
    "PermissionNotFound",
    "PermissionAlreadyExists",
]
