"""Domain exceptions - business logic errors."""

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

__all__ = [
    "UserNotFound",
    "UserAlreadyExists",
    "InvalidUserState",
    "RoleNotFound",
    "RoleAlreadyExists",
    "PermissionNotFound",
    "PermissionAlreadyExists",
]
