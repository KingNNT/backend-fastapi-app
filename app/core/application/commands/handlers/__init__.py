"""Command handlers - execute write operations."""

from app.core.application.commands.handlers.assignment_handlers import (
    AssignPermissionToRoleHandler,
    AssignPermissionToUserHandler,
    AssignRoleToUserHandler,
    IAssignmentRepository,
    RemovePermissionFromRoleHandler,
    RemovePermissionFromUserHandler,
    RemoveRoleFromUserHandler,
)
from app.core.application.commands.handlers.log_handlers import CreateLogHandler
from app.core.application.commands.handlers.permission_handlers import (
    CreatePermissionHandler,
    DeletePermissionHandler,
    UpdatePermissionHandler,
)
from app.core.application.commands.handlers.role_handlers import (
    CreateRoleHandler,
    DeleteRoleHandler,
    UpdateRoleHandler,
)
from app.core.application.commands.handlers.user_handlers import (
    CreateUserHandler,
    DeleteUserHandler,
    IPasswordHasher,
    UpdateUserHandler,
)

__all__ = [
    # User handlers
    "CreateUserHandler",
    "UpdateUserHandler",
    "DeleteUserHandler",
    "IPasswordHasher",
    # Log handlers
    "CreateLogHandler",
    # Role handlers
    "CreateRoleHandler",
    "UpdateRoleHandler",
    "DeleteRoleHandler",
    # Permission handlers
    "CreatePermissionHandler",
    "UpdatePermissionHandler",
    "DeletePermissionHandler",
    # Assignment handlers
    "AssignRoleToUserHandler",
    "RemoveRoleFromUserHandler",
    "AssignPermissionToUserHandler",
    "RemovePermissionFromUserHandler",
    "AssignPermissionToRoleHandler",
    "RemovePermissionFromRoleHandler",
    "IAssignmentRepository",
]
