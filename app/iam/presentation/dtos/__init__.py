"""IAM presentation DTOs."""

from app.iam.presentation.dtos.permission import (
    PermissionCreateRequest,
    PermissionListResponse,
    PermissionResponse,
    PermissionUpdateRequest,
)
from app.iam.presentation.dtos.role import (
    AssignRolePermissionRequest,
    RoleCreateRequest,
    RoleListResponse,
    RoleResponse,
    RoleUpdateRequest,
)
from app.iam.presentation.dtos.user import (
    AssignPermissionRequest,
    AssignRoleRequest,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)

__all__ = [
    # User DTOs
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserResponse",
    "UserListResponse",
    "AssignRoleRequest",
    "AssignPermissionRequest",
    # Role DTOs
    "RoleCreateRequest",
    "RoleUpdateRequest",
    "RoleResponse",
    "RoleListResponse",
    "AssignRolePermissionRequest",
    # Permission DTOs
    "PermissionCreateRequest",
    "PermissionUpdateRequest",
    "PermissionResponse",
    "PermissionListResponse",
]
