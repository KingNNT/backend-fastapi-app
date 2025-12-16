"""Permission queries."""

from app.core.application.queries.permission.get_permission import (
    GetPermissionByIdQuery,
    GetPermissionByNameQuery,
)
from app.core.application.queries.permission.list_permissions import (
    ListPermissionsQuery,
)

__all__ = [
    "GetPermissionByIdQuery",
    "GetPermissionByNameQuery",
    "ListPermissionsQuery",
]
