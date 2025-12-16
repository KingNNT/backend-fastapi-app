"""Value Objects - immutable objects defined by their attributes."""

from app.core.domain.value_objects.action import Action
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.log_id import LogId
from app.core.domain.value_objects.permission_id import PermissionId
from app.core.domain.value_objects.permission_name import PermissionName
from app.core.domain.value_objects.role_id import RoleId
from app.core.domain.value_objects.role_name import RoleName
from app.core.domain.value_objects.user_id import UserId
from app.core.domain.value_objects.username import Username

__all__ = [
    "UserId",
    "Email",
    "Username",
    "LogId",
    "Action",
    "RoleId",
    "RoleName",
    "PermissionId",
    "PermissionName",
]
