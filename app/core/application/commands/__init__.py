"""Commands - write operations (CQRS command side)."""

from app.core.application.commands.assignment import (
    AssignPermissionToRoleCommand,
    AssignPermissionToUserCommand,
    AssignRoleToUserCommand,
    RemovePermissionFromRoleCommand,
    RemovePermissionFromUserCommand,
    RemoveRoleFromUserCommand,
)
from app.core.application.commands.log import CreateLogCommand
from app.core.application.commands.permission import (
    CreatePermissionCommand,
    DeletePermissionCommand,
    UpdatePermissionCommand,
)
from app.core.application.commands.role import (
    CreateRoleCommand,
    DeleteRoleCommand,
    UpdateRoleCommand,
)
from app.core.application.commands.user import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)

__all__ = [
    # Assignment commands
    "AssignPermissionToRoleCommand",
    "AssignPermissionToUserCommand",
    "AssignRoleToUserCommand",
    "RemovePermissionFromRoleCommand",
    "RemovePermissionFromUserCommand",
    "RemoveRoleFromUserCommand",
    # Log commands
    "CreateLogCommand",
    # Permission commands
    "CreatePermissionCommand",
    "DeletePermissionCommand",
    "UpdatePermissionCommand",
    # Role commands
    "CreateRoleCommand",
    "DeleteRoleCommand",
    "UpdateRoleCommand",
    # User commands
    "CreateUserCommand",
    "DeleteUserCommand",
    "UpdateUserCommand",
]
