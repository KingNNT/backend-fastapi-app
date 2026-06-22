"""User API controller - V1."""

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.iam.application.commands.assignment import (
    AssignPermissionToUserCommand,
    AssignRoleToUserCommand,
    RemovePermissionFromUserCommand,
    RemoveRoleFromUserCommand,
)
from app.iam.application.commands.user import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from app.iam.application.queries.assignment import (
    GetUserEffectivePermissionsQuery,
    GetUserRolesQuery,
)
from app.iam.application.queries.user import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    ListUsersQuery,
)
from app.iam.domain.user.exceptions import UserNotFound
from app.iam.presentation.dependencies import (
    CreateUserHandlerDep,
    DeleteUserHandlerDep,
    GetUserByEmailHandlerDep,
    GetUserByIdHandlerDep,
    GetUserByUsernameHandlerDep,
    ListUsersHandlerDep,
    UpdateUserHandlerDep,
)
from app.iam.presentation.dependencies.handlers import (
    AssignPermissionToUserHandlerDep,
    AssignRoleToUserHandlerDep,
    GetUserEffectivePermissionsHandlerDep,
    GetUserRolesHandlerDep,
    RemovePermissionFromUserHandlerDep,
    RemoveRoleFromUserHandlerDep,
)
from app.iam.presentation.dependencies.repositories import IamUnitOfWorkDep
from app.iam.presentation.dtos import (
    AssignPermissionRequest,
    AssignRoleRequest,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.platform.web.response_dtos import (
    BadRequestResponse,
    ConflictResponse,
    CreatedResponse,
    NotFoundResponse,
    SuccessResponse,
    ValidationErrorResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatedResponse[UserResponse],
    responses={
        400: {"model": BadRequestResponse, "description": "Invalid input data"},
        409: {"model": ConflictResponse, "description": "User already exists"},
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
    },
)
async def create_user(
    request: UserCreateRequest,
    handler: CreateUserHandlerDep,
    uow: IamUnitOfWorkDep,
) -> JSONResponse:
    """Create a new user."""
    command = CreateUserCommand(
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name,
    )
    user_id = await handler.handle(command, uow)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "User created successfully",
            "data": {"id": user_id},
        },
    )


@router.get(
    "/",
    response_model=SuccessResponse[UserListResponse],
    summary="List Users",
    description="Retrieve a paginated list of users",
    responses={
        422: {
            "model": ValidationErrorResponse,
            "description": "Invalid query parameters",
        },
    },
)
async def list_users(
    handler: ListUsersHandlerDep,
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
) -> JSONResponse:
    """List all users with pagination."""
    query = ListUsersQuery(skip=skip, limit=limit)
    users = await handler.handle(query)

    user_responses = [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
        for user in users
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Users retrieved successfully",
            "data": {
                "data": user_responses,
                "skip": skip,
                "limit": limit,
                "count": len(users),
                "total": len(users) + skip,
            },
        },
    )


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def get_user(
    user_id: str,
    handler: GetUserByIdHandlerDep,
) -> JSONResponse:
    """Get a user by ID."""
    query = GetUserByIdQuery(user_id=user_id)
    user = await handler.handle(query)

    if user is None:
        raise UserNotFound(user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "User retrieved successfully",
            "data": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            },
        },
    )


@router.get(
    "/by-email/{email}",
    response_model=SuccessResponse[UserResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def get_user_by_email(
    email: str,
    handler: GetUserByEmailHandlerDep,
) -> JSONResponse:
    """Get a user by email."""
    query = GetUserByEmailQuery(email=email)
    user = await handler.handle(query)

    if user is None:
        raise UserNotFound(message=f"User with email '{email}' not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "User retrieved successfully",
            "data": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            },
        },
    )


@router.get(
    "/by-username/{username}",
    response_model=SuccessResponse[UserResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def get_user_by_username(
    username: str,
    handler: GetUserByUsernameHandlerDep,
) -> JSONResponse:
    """Get a user by username."""
    query = GetUserByUsernameQuery(username=username)
    user = await handler.handle(query)

    if user is None:
        raise UserNotFound(message=f"User with username '{username}' not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "User retrieved successfully",
            "data": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            },
        },
    )


@router.put(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    responses={
        400: {"model": BadRequestResponse, "description": "Invalid input data"},
        404: {"model": NotFoundResponse, "description": "User not found"},
        409: {"model": ConflictResponse, "description": "User already exists"},
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
    },
)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    handler: UpdateUserHandlerDep,
    uow: IamUnitOfWorkDep,
) -> JSONResponse:
    """Update a user."""
    command = UpdateUserCommand(
        user_id=user_id,
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name,
    )
    await handler.handle(command, uow)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "User updated successfully",
            "data": {"id": user_id},
        },
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def delete_user(
    user_id: str,
    handler: DeleteUserHandlerDep,
    uow: IamUnitOfWorkDep,
) -> JSONResponse:
    """Delete a user (soft delete)."""
    command = DeleteUserCommand(user_id=user_id)
    await handler.handle(command, uow)

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )


# User-Role assignment endpoints
@router.get(
    "/{user_id}/roles",
    response_model=SuccessResponse[list],
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def get_user_roles(
    user_id: str,
    handler: GetUserRolesHandlerDep,
) -> JSONResponse:
    """Get all roles assigned to a user."""
    query = GetUserRolesQuery(user_id=user_id)
    roles = await handler.handle(query)

    role_responses = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat(),
        }
        for role in roles
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "User roles retrieved successfully",
            "data": role_responses,
        },
    )


@router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": NotFoundResponse, "description": "User or role not found"},
        409: {"model": ConflictResponse, "description": "Role already assigned"},
    },
)
async def assign_role_to_user(
    user_id: str,
    request: AssignRoleRequest,
    handler: AssignRoleToUserHandlerDep,
) -> JSONResponse:
    """Assign a role to a user."""
    command = AssignRoleToUserCommand(
        user_id=user_id,
        role_id=request.role_id,
    )
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Role assigned to user successfully",
            "data": {
                "user_id": user_id,
                "role_id": request.role_id,
            },
        },
    )


@router.delete(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": NotFoundResponse, "description": "Assignment not found"},
    },
)
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    handler: RemoveRoleFromUserHandlerDep,
) -> JSONResponse:
    """Remove a role from a user."""
    command = RemoveRoleFromUserCommand(
        user_id=user_id,
        role_id=role_id,
    )
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )


# User-Permission assignment endpoints
@router.get(
    "/{user_id}/permissions",
    response_model=SuccessResponse[list],
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def get_user_effective_permissions(
    user_id: str,
    handler: GetUserEffectivePermissionsHandlerDep,
) -> JSONResponse:
    """Get all effective permissions for a user (includes role permissions)."""
    query = GetUserEffectivePermissionsQuery(user_id=user_id)
    permissions = await handler.handle(query)

    permission_responses = [
        {
            "id": perm.id,
            "name": perm.name,
            "description": perm.description,
            "created_at": perm.created_at.isoformat(),
            "updated_at": perm.updated_at.isoformat(),
        }
        for perm in permissions
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "User permissions retrieved successfully",
            "data": permission_responses,
        },
    )


@router.post(
    "/{user_id}/permissions",
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": NotFoundResponse, "description": "User or permission not found"},
        409: {"model": ConflictResponse, "description": "Permission already assigned"},
    },
)
async def assign_permission_to_user(
    user_id: str,
    request: AssignPermissionRequest,
    handler: AssignPermissionToUserHandlerDep,
) -> JSONResponse:
    """Assign a direct permission to a user."""
    command = AssignPermissionToUserCommand(
        user_id=user_id,
        permission_id=request.permission_id,
    )
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Permission assigned to user successfully",
            "data": {
                "user_id": user_id,
                "permission_id": request.permission_id,
            },
        },
    )


@router.delete(
    "/{user_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": NotFoundResponse, "description": "Assignment not found"},
    },
)
async def remove_permission_from_user(
    user_id: str,
    permission_id: str,
    handler: RemovePermissionFromUserHandlerDep,
) -> JSONResponse:
    """Remove a direct permission from a user."""
    command = RemovePermissionFromUserCommand(
        user_id=user_id,
        permission_id=permission_id,
    )
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
