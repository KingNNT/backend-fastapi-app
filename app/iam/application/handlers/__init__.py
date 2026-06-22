"""IAM application handlers — command and query handlers."""

from app.iam.application.handlers.assignment_handlers import (
    AssignPermissionToRoleHandler,
    AssignPermissionToUserHandler,
    AssignRoleToUserHandler,
    RemovePermissionFromRoleHandler,
    RemovePermissionFromUserHandler,
    RemoveRoleFromUserHandler,
)
from app.iam.application.handlers.assignment_query_handlers import (
    GetRolePermissionsHandler,
    GetUserEffectivePermissionsHandler,
    GetUserRolesHandler,
)
from app.iam.application.handlers.permission_handlers import (
    CreatePermissionHandler,
    DeletePermissionHandler,
    UpdatePermissionHandler,
)
from app.iam.application.handlers.permission_query_handlers import (
    GetPermissionByIdHandler,
    GetPermissionByNameHandler,
    ListPermissionsHandler,
)
from app.iam.application.handlers.role_handlers import (
    CreateRoleHandler,
    DeleteRoleHandler,
    UpdateRoleHandler,
)
from app.iam.application.handlers.role_query_handlers import (
    GetRoleByIdHandler,
    GetRoleByNameHandler,
    ListRolesHandler,
)
from app.iam.application.handlers.user_handlers import (
    CreateUserHandler,
    DeleteUserHandler,
    UpdateUserHandler,
)
from app.iam.application.handlers.user_query_handlers import (
    GetUserByEmailHandler,
    GetUserByIdHandler,
    GetUserByUsernameHandler,
    ListUsersHandler,
)

__all__ = [
    # User command handlers
    "CreateUserHandler",
    "UpdateUserHandler",
    "DeleteUserHandler",
    # User query handlers
    "GetUserByIdHandler",
    "GetUserByEmailHandler",
    "GetUserByUsernameHandler",
    "ListUsersHandler",
    # Role command handlers
    "CreateRoleHandler",
    "UpdateRoleHandler",
    "DeleteRoleHandler",
    # Role query handlers
    "GetRoleByIdHandler",
    "GetRoleByNameHandler",
    "ListRolesHandler",
    # Permission command handlers
    "CreatePermissionHandler",
    "UpdatePermissionHandler",
    "DeletePermissionHandler",
    # Permission query handlers
    "GetPermissionByIdHandler",
    "GetPermissionByNameHandler",
    "ListPermissionsHandler",
    # Assignment command handlers
    "AssignRoleToUserHandler",
    "RemoveRoleFromUserHandler",
    "AssignPermissionToUserHandler",
    "RemovePermissionFromUserHandler",
    "AssignPermissionToRoleHandler",
    "RemovePermissionFromRoleHandler",
    # Assignment query handlers
    "GetUserRolesHandler",
    "GetUserEffectivePermissionsHandler",
    "GetRolePermissionsHandler",
]
