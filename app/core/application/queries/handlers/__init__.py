"""Query handlers - execute read operations."""

from app.core.application.queries.handlers.assignment_handlers import (
    GetRolePermissionsHandler,
    GetUserEffectivePermissionsHandler,
    GetUserRolesHandler,
    IAssignmentQueryRepository,
    IPermissionReadModelRepository,
    IRoleReadModelRepository,
)
from app.core.application.queries.handlers.log_handlers import (
    GetLogByIdHandler,
    ILogReadModelRepository,
    ListLogsByActionHandler,
    ListLogsByDateRangeHandler,
    ListLogsByUserHandler,
    ListLogsHandler,
)
from app.core.application.queries.handlers.permission_handlers import (
    GetPermissionByIdHandler,
    GetPermissionByNameHandler,
    ListPermissionsHandler,
)
from app.core.application.queries.handlers.role_handlers import (
    GetRoleByIdHandler,
    GetRoleByNameHandler,
    ListRolesHandler,
)
from app.core.application.queries.handlers.user_handlers import (
    GetUserByEmailHandler,
    GetUserByIdHandler,
    GetUserByUsernameHandler,
    IUserReadModelRepository,
    ListUsersHandler,
)

__all__ = [
    # User handlers
    "GetUserByIdHandler",
    "GetUserByEmailHandler",
    "GetUserByUsernameHandler",
    "ListUsersHandler",
    "IUserReadModelRepository",
    # Log handlers
    "GetLogByIdHandler",
    "ListLogsHandler",
    "ListLogsByUserHandler",
    "ListLogsByActionHandler",
    "ListLogsByDateRangeHandler",
    "ILogReadModelRepository",
    # Role handlers
    "GetRoleByIdHandler",
    "GetRoleByNameHandler",
    "ListRolesHandler",
    "IRoleReadModelRepository",
    # Permission handlers
    "GetPermissionByIdHandler",
    "GetPermissionByNameHandler",
    "ListPermissionsHandler",
    "IPermissionReadModelRepository",
    # Assignment handlers
    "GetUserRolesHandler",
    "GetUserEffectivePermissionsHandler",
    "GetRolePermissionsHandler",
    "IAssignmentQueryRepository",
]
