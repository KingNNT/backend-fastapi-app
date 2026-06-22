"""IAM presentation dependency providers - handlers."""

from typing import Annotated

from fastapi import Depends

from app.iam.application.handlers import (
    AssignPermissionToRoleHandler,
    AssignPermissionToUserHandler,
    AssignRoleToUserHandler,
    CreatePermissionHandler,
    CreateRoleHandler,
    CreateUserHandler,
    DeletePermissionHandler,
    DeleteRoleHandler,
    DeleteUserHandler,
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
    ListPermissionsHandler,
    ListRolesHandler,
    ListUsersHandler,
    RemovePermissionFromRoleHandler,
    RemovePermissionFromUserHandler,
    RemoveRoleFromUserHandler,
    UpdatePermissionHandler,
    UpdateRoleHandler,
    UpdateUserHandler,
)
from app.iam.application.interfaces.password_hasher import IPasswordHasher
from app.iam.presentation.dependencies.repositories import (
    IamUnitOfWorkDep,
    PermissionReadModelRepositoryDep,
    RoleReadModelRepositoryDep,
    UserReadModelRepositoryDep,
)
from app.platform.messaging.services import get_password_hasher

PasswordHasherDep = Annotated[IPasswordHasher, Depends(get_password_hasher)]


# ─── User Command Handlers ───────────────────────────────────────────────────
def get_create_user_handler(
    password_hasher: IPasswordHasher = Depends(PasswordHasherDep),
) -> CreateUserHandler:
    """Get CreateUserHandler. Receives UoW via Depends in handle()."""
    return CreateUserHandler(password_hasher=password_hasher)


def get_update_user_handler(
    password_hasher: IPasswordHasher = Depends(PasswordHasherDep),
) -> UpdateUserHandler:
    """Get UpdateUserHandler."""
    return UpdateUserHandler(password_hasher=password_hasher)


def get_delete_user_handler() -> DeleteUserHandler:
    return DeleteUserHandler()


# ─── User Query Handlers ─────────────────────────────────────────────────────
def get_user_by_id_handler(
    repository=Depends(UserReadModelRepositoryDep),
) -> GetUserByIdHandler:
    return GetUserByIdHandler(repository=repository)


def get_user_by_email_handler(
    repository=Depends(UserReadModelRepositoryDep),
) -> GetUserByEmailHandler:
    return GetUserByEmailHandler(repository=repository)


def get_user_by_username_handler(
    repository=Depends(UserReadModelRepositoryDep),
) -> GetUserByUsernameHandler:
    return GetUserByUsernameHandler(repository=repository)


def get_list_users_handler(
    repository=Depends(UserReadModelRepositoryDep),
) -> ListUsersHandler:
    return ListUsersHandler(repository=repository)


# ─── Role Command Handlers ───────────────────────────────────────────────────
def get_create_role_handler() -> CreateRoleHandler:
    return CreateRoleHandler()


def get_update_role_handler() -> UpdateRoleHandler:
    return UpdateRoleHandler()


def get_delete_role_handler() -> DeleteRoleHandler:
    return DeleteRoleHandler()


# ─── Role Query Handlers ─────────────────────────────────────────────────────
def get_role_by_id_handler(
    repository=Depends(RoleReadModelRepositoryDep),
) -> GetRoleByIdHandler:
    return GetRoleByIdHandler(repository=repository)


def get_role_by_name_handler(
    repository=Depends(RoleReadModelRepositoryDep),
) -> GetRoleByNameHandler:
    return GetRoleByNameHandler(repository=repository)


def get_list_roles_handler(
    repository=Depends(RoleReadModelRepositoryDep),
) -> ListRolesHandler:
    return ListRolesHandler(repository=repository)


# ─── Permission Command Handlers ─────────────────────────────────────────────
def get_create_permission_handler() -> CreatePermissionHandler:
    return CreatePermissionHandler()


def get_update_permission_handler() -> UpdatePermissionHandler:
    return UpdatePermissionHandler()


def get_delete_permission_handler() -> DeletePermissionHandler:
    return DeletePermissionHandler()


# ─── Permission Query Handlers ───────────────────────────────────────────────
def get_permission_by_id_handler(
    repository=Depends(PermissionReadModelRepositoryDep),
) -> GetPermissionByIdHandler:
    return GetPermissionByIdHandler(repository=repository)


def get_permission_by_name_handler(
    repository=Depends(PermissionReadModelRepositoryDep),
) -> GetPermissionByNameHandler:
    return GetPermissionByNameHandler(repository=repository)


def get_list_permissions_handler(
    repository=Depends(PermissionReadModelRepositoryDep),
) -> ListPermissionsHandler:
    return ListPermissionsHandler(repository=repository)


# ─── Assignment Command Handlers (no constructor args) ──────────────────────
def get_assign_role_to_user_handler() -> AssignRoleToUserHandler:
    return AssignRoleToUserHandler()


def get_remove_role_from_user_handler() -> RemoveRoleFromUserHandler:
    return RemoveRoleFromUserHandler()


def get_assign_permission_to_user_handler() -> AssignPermissionToUserHandler:
    return AssignPermissionToUserHandler()


def get_remove_permission_from_user_handler() -> RemovePermissionFromUserHandler:
    return RemovePermissionFromUserHandler()


def get_assign_permission_to_role_handler() -> AssignPermissionToRoleHandler:
    return AssignPermissionToRoleHandler()


def get_remove_permission_from_role_handler() -> RemovePermissionFromRoleHandler:
    return RemovePermissionFromRoleHandler()


# ─── Assignment Query Handlers ───────────────────────────────────────────────
def get_user_roles_handler(
    uow=Depends(IamUnitOfWorkDep),
    role_repo=Depends(RoleReadModelRepositoryDep),
) -> GetUserRolesHandler:
    return GetUserRolesHandler(
        assignment_repository=uow.assignments,
        role_repository=role_repo,
    )


def get_user_effective_permissions_handler(
    uow=Depends(IamUnitOfWorkDep),
    permission_repo=Depends(PermissionReadModelRepositoryDep),
) -> GetUserEffectivePermissionsHandler:
    return GetUserEffectivePermissionsHandler(
        assignment_repository=uow.assignments,
        permission_repository=permission_repo,
    )


def get_role_permissions_handler(
    uow=Depends(IamUnitOfWorkDep),
    permission_repo=Depends(PermissionReadModelRepositoryDep),
) -> GetRolePermissionsHandler:
    return GetRolePermissionsHandler(
        assignment_repository=uow.assignments,
        permission_repository=permission_repo,
    )


# ─── Type aliases ────────────────────────────────────────────────────────────
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

CreateRoleHandlerDep = Annotated[CreateRoleHandler, Depends(get_create_role_handler)]
UpdateRoleHandlerDep = Annotated[UpdateRoleHandler, Depends(get_update_role_handler)]
DeleteRoleHandlerDep = Annotated[DeleteRoleHandler, Depends(get_delete_role_handler)]
GetRoleByIdHandlerDep = Annotated[GetRoleByIdHandler, Depends(get_role_by_id_handler)]
GetRoleByNameHandlerDep = Annotated[
    GetRoleByNameHandler, Depends(get_role_by_name_handler)
]
ListRolesHandlerDep = Annotated[ListRolesHandler, Depends(get_list_roles_handler)]

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
    GetUserEffectivePermissionsHandler,
    Depends(get_user_effective_permissions_handler),
]
GetRolePermissionsHandlerDep = Annotated[
    GetRolePermissionsHandler, Depends(get_role_permissions_handler)
]
