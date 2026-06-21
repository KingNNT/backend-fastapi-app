"""Permission queries."""

from app.iam.application.queries.permission.get_permission import (
    GetPermissionByIdQuery,
    GetPermissionByNameQuery,
)
from app.iam.application.queries.permission.list_permissions import (
    ListPermissionsQuery,
)

__all__ = [
    "GetPermissionByIdQuery",
    "GetPermissionByNameQuery",
    "ListPermissionsQuery",
]
