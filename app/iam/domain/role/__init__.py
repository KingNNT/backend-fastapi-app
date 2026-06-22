"""Role aggregate — domain layer for Role concept."""

from app.iam.domain.role.aggregate import RoleAggregate
from app.iam.domain.role.entity import Role
from app.iam.domain.role.events import (
    PermissionAssignedToRole,
    PermissionRemovedFromRole,
    RoleAssignedToUser,
    RoleCreated,
    RoleDeleted,
    RoleRemovedFromUser,
    RoleUpdated,
)
from app.iam.domain.role.exceptions import (
    RoleAlreadyExists,
    RoleNotFound,
)
from app.iam.domain.role.repository import (
    IRoleReadRepository,
    IRoleWriteRepository,
)
from app.iam.domain.role.value_objects import RoleName

__all__ = [
    "RoleAggregate",
    "Role",
    "RoleName",
    "RoleCreated",
    "RoleUpdated",
    "RoleDeleted",
    "PermissionAssignedToRole",
    "PermissionRemovedFromRole",
    "RoleAssignedToUser",
    "RoleRemovedFromUser",
    "RoleNotFound",
    "RoleAlreadyExists",
    "IRoleWriteRepository",
    "IRoleReadRepository",
]
