"""Dependency injection for CQRS handlers."""

from typing import Annotated

from fastapi import Depends

from app.core.application.commands.handlers import (
    AssignPermissionToRoleHandler,
    AssignPermissionToUserHandler,
    AssignRoleToUserHandler,
    CreateLogHandler,
    CreatePermissionHandler,
    CreateRoleHandler,
    CreateUserHandler,
    DeletePermissionHandler,
    DeleteRoleHandler,
    DeleteUserHandler,
    RemovePermissionFromRoleHandler,
    RemovePermissionFromUserHandler,
    RemoveRoleFromUserHandler,
    UpdatePermissionHandler,
    UpdateRoleHandler,
    UpdateUserHandler,
)
from app.core.application.queries.handlers import (
    GetLogByIdHandler,
    GetPermissionByIdHandler,
    GetPermissionByNameHandler,
    GetRoleByIdHandler,
    GetRoleByNameHandler,
    GetRolePermissionsHandler,
    GetUserByEmailHandler,
    GetUserByIdHandler,
    GetUserByUsernameHandler,
    GetUserEffectivePermissionsHandler,
    GetUserRolesHandler,
    ListLogsByUserHandler,
    ListLogsHandler,
    ListPermissionsHandler,
    ListRolesHandler,
    ListUsersHandler,
)
from app.presentation.dependencies.repositories import (
    get_assignment_repository,
    get_log_read_model_repository,
    get_log_repository,
    get_permission_read_model_repository,
    get_role_read_model_repository,
    get_user_read_model_repository,
)
from app.presentation.dependencies.services import (
    get_event_bus,
    get_password_hasher,
)


# User Command Handlers
def get_create_user_handler(
    password_hasher=Depends(get_password_hasher),
) -> CreateUserHandler:
    """Get CreateUserHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return CreateUserHandler(password_hasher=password_hasher)


def get_update_user_handler(
    password_hasher=Depends(get_password_hasher),
) -> UpdateUserHandler:
    """Get UpdateUserHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return UpdateUserHandler(password_hasher=password_hasher)


def get_delete_user_handler() -> DeleteUserHandler:
    """Get DeleteUserHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return DeleteUserHandler()


# User Query Handlers
def get_user_by_id_handler(
    repository=Depends(get_user_read_model_repository),
) -> GetUserByIdHandler:
    """Get GetUserByIdHandler instance."""
    return GetUserByIdHandler(repository=repository)


def get_user_by_email_handler(
    repository=Depends(get_user_read_model_repository),
) -> GetUserByEmailHandler:
    """Get GetUserByEmailHandler instance."""
    return GetUserByEmailHandler(repository=repository)


def get_user_by_username_handler(
    repository=Depends(get_user_read_model_repository),
) -> GetUserByUsernameHandler:
    """Get GetUserByUsernameHandler instance."""
    return GetUserByUsernameHandler(repository=repository)


def get_list_users_handler(
    repository=Depends(get_user_read_model_repository),
) -> ListUsersHandler:
    """Get ListUsersHandler instance."""
    return ListUsersHandler(repository=repository)


# Log Command Handlers
def get_create_log_handler(
    repository=Depends(get_log_repository),
    event_bus=Depends(get_event_bus),
) -> CreateLogHandler:
    """Get CreateLogHandler instance."""
    return CreateLogHandler(
        repository=repository,
        event_bus=event_bus,
    )


# Log Query Handlers
def get_log_by_id_handler(
    repository=Depends(get_log_read_model_repository),
) -> GetLogByIdHandler:
    """Get GetLogByIdHandler instance."""
    return GetLogByIdHandler(repository=repository)


def get_list_logs_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsHandler:
    """Get ListLogsHandler instance."""
    return ListLogsHandler(repository=repository)


def get_list_logs_by_user_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsByUserHandler:
    """Get ListLogsByUserHandler instance."""
    return ListLogsByUserHandler(repository=repository)


# Role Command Handlers
def get_create_role_handler() -> CreateRoleHandler:
    """Get CreateRoleHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return CreateRoleHandler()


def get_update_role_handler() -> UpdateRoleHandler:
    """Get UpdateRoleHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return UpdateRoleHandler()


def get_delete_role_handler() -> DeleteRoleHandler:
    """Get DeleteRoleHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return DeleteRoleHandler()


# Role Query Handlers
def get_role_by_id_handler(
    repository=Depends(get_role_read_model_repository),
) -> GetRoleByIdHandler:
    """Get GetRoleByIdHandler instance."""
    return GetRoleByIdHandler(repository=repository)


def get_role_by_name_handler(
    repository=Depends(get_role_read_model_repository),
) -> GetRoleByNameHandler:
    """Get GetRoleByNameHandler instance."""
    return GetRoleByNameHandler(repository=repository)


def get_list_roles_handler(
    repository=Depends(get_role_read_model_repository),
) -> ListRolesHandler:
    """Get ListRolesHandler instance."""
    return ListRolesHandler(repository=repository)


# Permission Command Handlers
def get_create_permission_handler() -> CreatePermissionHandler:
    """Get CreatePermissionHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return CreatePermissionHandler()


def get_update_permission_handler() -> UpdatePermissionHandler:
    """Get UpdatePermissionHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return UpdatePermissionHandler()


def get_delete_permission_handler() -> DeletePermissionHandler:
    """Get DeletePermissionHandler instance.

    Handler receives UoW as parameter to handle() method.
    Repositories are accessed via UoW properties.
    """
    return DeletePermissionHandler()


# Permission Query Handlers
def get_permission_by_id_handler(
    repository=Depends(get_permission_read_model_repository),
) -> GetPermissionByIdHandler:
    """Get GetPermissionByIdHandler instance."""
    return GetPermissionByIdHandler(repository=repository)


def get_permission_by_name_handler(
    repository=Depends(get_permission_read_model_repository),
) -> GetPermissionByNameHandler:
    """Get GetPermissionByNameHandler instance."""
    return GetPermissionByNameHandler(repository=repository)


def get_list_permissions_handler(
    repository=Depends(get_permission_read_model_repository),
) -> ListPermissionsHandler:
    """Get ListPermissionsHandler instance."""
    return ListPermissionsHandler(repository=repository)


# Assignment Command Handlers
def get_assign_role_to_user_handler(
    assignment_repository=Depends(get_assignment_repository),
    event_bus=Depends(get_event_bus),
) -> AssignRoleToUserHandler:
    """Get AssignRoleToUserHandler instance."""
    return AssignRoleToUserHandler(
        assignment_repository=assignment_repository,
        event_bus=event_bus,
    )


def get_remove_role_from_user_handler(
    assignment_repository=Depends(get_assignment_repository),
    event_bus=Depends(get_event_bus),
) -> RemoveRoleFromUserHandler:
    """Get RemoveRoleFromUserHandler instance."""
    return RemoveRoleFromUserHandler(
        assignment_repository=assignment_repository,
        event_bus=event_bus,
    )


def get_assign_permission_to_user_handler(
    assignment_repository=Depends(get_assignment_repository),
    event_bus=Depends(get_event_bus),
) -> AssignPermissionToUserHandler:
    """Get AssignPermissionToUserHandler instance."""
    return AssignPermissionToUserHandler(
        assignment_repository=assignment_repository,
        event_bus=event_bus,
    )


def get_remove_permission_from_user_handler(
    assignment_repository=Depends(get_assignment_repository),
    event_bus=Depends(get_event_bus),
) -> RemovePermissionFromUserHandler:
    """Get RemovePermissionFromUserHandler instance."""
    return RemovePermissionFromUserHandler(
        assignment_repository=assignment_repository,
        event_bus=event_bus,
    )


def get_assign_permission_to_role_handler(
    assignment_repository=Depends(get_assignment_repository),
    event_bus=Depends(get_event_bus),
) -> AssignPermissionToRoleHandler:
    """Get AssignPermissionToRoleHandler instance."""
    return AssignPermissionToRoleHandler(
        assignment_repository=assignment_repository,
        event_bus=event_bus,
    )


def get_remove_permission_from_role_handler(
    assignment_repository=Depends(get_assignment_repository),
    event_bus=Depends(get_event_bus),
) -> RemovePermissionFromRoleHandler:
    """Get RemovePermissionFromRoleHandler instance."""
    return RemovePermissionFromRoleHandler(
        assignment_repository=assignment_repository,
        event_bus=event_bus,
    )


# Assignment Query Handlers
def get_user_roles_handler(
    assignment_repository=Depends(get_assignment_repository),
    role_repository=Depends(get_role_read_model_repository),
) -> GetUserRolesHandler:
    """Get GetUserRolesHandler instance."""
    return GetUserRolesHandler(
        assignment_repository=assignment_repository,
        role_repository=role_repository,
    )


def get_user_effective_permissions_handler(
    assignment_repository=Depends(get_assignment_repository),
    permission_repository=Depends(get_permission_read_model_repository),
) -> GetUserEffectivePermissionsHandler:
    """Get GetUserEffectivePermissionsHandler instance."""
    return GetUserEffectivePermissionsHandler(
        assignment_repository=assignment_repository,
        permission_repository=permission_repository,
    )


def get_role_permissions_handler(
    assignment_repository=Depends(get_assignment_repository),
    permission_repository=Depends(get_permission_read_model_repository),
) -> GetRolePermissionsHandler:
    """Get GetRolePermissionsHandler instance."""
    return GetRolePermissionsHandler(
        assignment_repository=assignment_repository,
        permission_repository=permission_repository,
    )


# Type aliases for dependency injection
CreateUserHandlerDep = Annotated[CreateUserHandler, Depends(get_create_user_handler)]
UpdateUserHandlerDep = Annotated[UpdateUserHandler, Depends(get_update_user_handler)]
DeleteUserHandlerDep = Annotated[DeleteUserHandler, Depends(get_delete_user_handler)]
GetUserByIdHandlerDep = Annotated[GetUserByIdHandler, Depends(get_user_by_id_handler)]
GetUserByEmailHandlerDep = Annotated[
    GetUserByEmailHandler, Depends(get_user_by_email_handler)
]
GetUserByUsernameHandlerDep = Annotated[
    GetUserByUsernameHandler, Depends(get_user_by_username_handler)
]
ListUsersHandlerDep = Annotated[ListUsersHandler, Depends(get_list_users_handler)]
CreateLogHandlerDep = Annotated[CreateLogHandler, Depends(get_create_log_handler)]
GetLogByIdHandlerDep = Annotated[GetLogByIdHandler, Depends(get_log_by_id_handler)]
ListLogsHandlerDep = Annotated[ListLogsHandler, Depends(get_list_logs_handler)]
ListLogsByUserHandlerDep = Annotated[
    ListLogsByUserHandler, Depends(get_list_logs_by_user_handler)
]

# Role handler type aliases
CreateRoleHandlerDep = Annotated[CreateRoleHandler, Depends(get_create_role_handler)]
UpdateRoleHandlerDep = Annotated[UpdateRoleHandler, Depends(get_update_role_handler)]
DeleteRoleHandlerDep = Annotated[DeleteRoleHandler, Depends(get_delete_role_handler)]
GetRoleByIdHandlerDep = Annotated[GetRoleByIdHandler, Depends(get_role_by_id_handler)]
GetRoleByNameHandlerDep = Annotated[
    GetRoleByNameHandler, Depends(get_role_by_name_handler)
]
ListRolesHandlerDep = Annotated[ListRolesHandler, Depends(get_list_roles_handler)]

# Permission handler type aliases
CreatePermissionHandlerDep = Annotated[
    CreatePermissionHandler, Depends(get_create_permission_handler)
]
UpdatePermissionHandlerDep = Annotated[
    UpdatePermissionHandler, Depends(get_update_permission_handler)
]
DeletePermissionHandlerDep = Annotated[
    DeletePermissionHandler, Depends(get_delete_permission_handler)
]
GetPermissionByIdHandlerDep = Annotated[
    GetPermissionByIdHandler, Depends(get_permission_by_id_handler)
]
GetPermissionByNameHandlerDep = Annotated[
    GetPermissionByNameHandler, Depends(get_permission_by_name_handler)
]
ListPermissionsHandlerDep = Annotated[
    ListPermissionsHandler, Depends(get_list_permissions_handler)
]

# Assignment handler type aliases
AssignRoleToUserHandlerDep = Annotated[
    AssignRoleToUserHandler, Depends(get_assign_role_to_user_handler)
]
RemoveRoleFromUserHandlerDep = Annotated[
    RemoveRoleFromUserHandler, Depends(get_remove_role_from_user_handler)
]
AssignPermissionToUserHandlerDep = Annotated[
    AssignPermissionToUserHandler, Depends(get_assign_permission_to_user_handler)
]
RemovePermissionFromUserHandlerDep = Annotated[
    RemovePermissionFromUserHandler, Depends(get_remove_permission_from_user_handler)
]
AssignPermissionToRoleHandlerDep = Annotated[
    AssignPermissionToRoleHandler, Depends(get_assign_permission_to_role_handler)
]
RemovePermissionFromRoleHandlerDep = Annotated[
    RemovePermissionFromRoleHandler, Depends(get_remove_permission_from_role_handler)
]
GetUserRolesHandlerDep = Annotated[GetUserRolesHandler, Depends(get_user_roles_handler)]
GetUserEffectivePermissionsHandlerDep = Annotated[
    GetUserEffectivePermissionsHandler, Depends(get_user_effective_permissions_handler)
]
GetRolePermissionsHandlerDep = Annotated[
    GetRolePermissionsHandler, Depends(get_role_permissions_handler)
]
