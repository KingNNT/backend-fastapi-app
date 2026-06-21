"""Value Objects - immutable objects defined by their attributes."""

from app.core.domain.value_objects.action import Action
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.permission_name import PermissionName
from app.core.domain.value_objects.role_name import RoleName
from app.core.domain.value_objects.username import Username

__all__ = [
    "Email",
    "Username",
    "Action",
    "RoleName",
    "PermissionName",
]
