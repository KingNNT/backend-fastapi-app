"""PostgreSQL persistence models."""

from app.infrastructure.persistence.postgresql.models.base import BaseModel
from app.infrastructure.persistence.postgresql.models.permission import PermissionModel
from app.infrastructure.persistence.postgresql.models.role import RoleModel
from app.infrastructure.persistence.postgresql.models.role_has_permissions import (
    RoleHasPermissionsModel,
)
from app.infrastructure.persistence.postgresql.models.user import UserModel
from app.infrastructure.persistence.postgresql.models.user_has_permission import (
    UserHasPermissionModel,
)
from app.infrastructure.persistence.postgresql.models.user_has_role import (
    UserHasRoleModel,
)

__all__ = [
    "BaseModel",
    "PermissionModel",
    "RoleHasPermissionsModel",
    "RoleModel",
    "UserHasPermissionModel",
    "UserHasRoleModel",
    "UserModel",
]
