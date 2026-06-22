"""Presentation layer DTOs."""

from app.platform.web.response_dtos import (
    BadRequestResponse,
    ConflictResponse,
    CreatedResponse,
    ErrorResponse,
    NotFoundResponse,
    SuccessResponse,
    ValidationErrorResponse,
)
from app.presentation.dtos.log import (
    LogCreateRequest,
    LogListResponse,
    LogResponse,
)
from app.presentation.dtos.permission import (
    PermissionCreateRequest,
    PermissionListResponse,
    PermissionResponse,
    PermissionUpdateRequest,
)
from app.presentation.dtos.role import (
    AssignPermissionRequest,
    RoleCreateRequest,
    RoleListResponse,
    RoleResponse,
    RoleUpdateRequest,
)
from app.presentation.dtos.system import (
    HealthCheckResponse,
    VersionResponse,
)
from app.presentation.dtos.user import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)

__all__ = [
    # Log DTOs
    "LogCreateRequest",
    "LogListResponse",
    "LogResponse",
    # Permission DTOs
    "PermissionCreateRequest",
    "PermissionListResponse",
    "PermissionResponse",
    "PermissionUpdateRequest",
    # Response DTOs
    "BadRequestResponse",
    "ConflictResponse",
    "CreatedResponse",
    "ErrorResponse",
    "NotFoundResponse",
    "SuccessResponse",
    "ValidationErrorResponse",
    # Role DTOs
    "AssignPermissionRequest",
    "RoleCreateRequest",
    "RoleListResponse",
    "RoleResponse",
    "RoleUpdateRequest",
    # System DTOs
    "HealthCheckResponse",
    "VersionResponse",
    # User DTOs
    "UserCreateRequest",
    "UserListResponse",
    "UserResponse",
    "UserUpdateRequest",
]
