"""Queries - read operations (CQRS query side)."""

from app.core.application.queries.assignment import (
    GetRolePermissionsQuery,
    GetUserEffectivePermissionsQuery,
    GetUserRolesQuery,
)
from app.core.application.queries.log import (
    GetLogByIdQuery,
    ListLogsByActionQuery,
    ListLogsByDateRangeQuery,
    ListLogsByUserQuery,
    ListLogsQuery,
)
from app.core.application.queries.permission import (
    GetPermissionByIdQuery,
    GetPermissionByNameQuery,
    ListPermissionsQuery,
)
from app.core.application.queries.role import (
    GetRoleByIdQuery,
    GetRoleByNameQuery,
    ListRolesQuery,
)
from app.core.application.queries.user import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    ListUsersQuery,
)

__all__ = [
    # Assignment queries
    "GetRolePermissionsQuery",
    "GetUserEffectivePermissionsQuery",
    "GetUserRolesQuery",
    # Log queries
    "GetLogByIdQuery",
    "ListLogsByActionQuery",
    "ListLogsByDateRangeQuery",
    "ListLogsByUserQuery",
    "ListLogsQuery",
    # Permission queries
    "GetPermissionByIdQuery",
    "GetPermissionByNameQuery",
    "ListPermissionsQuery",
    # Role queries
    "GetRoleByIdQuery",
    "GetRoleByNameQuery",
    "ListRolesQuery",
    # User queries
    "GetUserByEmailQuery",
    "GetUserByIdQuery",
    "GetUserByUsernameQuery",
    "ListUsersQuery",
]
