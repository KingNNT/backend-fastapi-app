"""Permission aggregate — domain layer for Permission concept."""

from app.iam.domain.permission.aggregate import PermissionAggregate
from app.iam.domain.permission.entity import Permission
from app.iam.domain.permission.events import (
    PermissionAssignedToUser,
    PermissionCreated,
    PermissionDeleted,
    PermissionRemovedFromUser,
    PermissionUpdated,
)
from app.iam.domain.permission.exceptions import (
    PermissionAlreadyExists,
    PermissionNotFound,
)
from app.iam.domain.permission.repository import (
    IPermissionReadRepository,
    IPermissionWriteRepository,
)
from app.iam.domain.permission.value_objects import PermissionName

__all__ = [
    "PermissionAggregate",
    "Permission",
    "PermissionName",
    "PermissionCreated",
    "PermissionUpdated",
    "PermissionDeleted",
    "PermissionAssignedToUser",
    "PermissionRemovedFromUser",
    "PermissionNotFound",
    "PermissionAlreadyExists",
    "IPermissionWriteRepository",
    "IPermissionReadRepository",
]
