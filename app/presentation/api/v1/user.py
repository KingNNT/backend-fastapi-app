"""User API controller - V1."""

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.core.application.commands.user import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from app.core.application.queries.user import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    ListUsersQuery,
)
from app.core.domain.exceptions.user import UserNotFound
from app.presentation.dependencies import (
    CreateUserHandlerDep,
    DeleteUserHandlerDep,
    GetUserByEmailHandlerDep,
    GetUserByIdHandlerDep,
    GetUserByUsernameHandlerDep,
    ListUsersHandlerDep,
    UpdateUserHandlerDep,
)
from app.presentation.dtos import (
    BadRequestResponse,
    ConflictResponse,
    CreatedResponse,
    NotFoundResponse,
    SuccessResponse,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
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
) -> JSONResponse:
    """Create a new user."""
    command = CreateUserCommand(
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name,
    )
    user_id = await handler.handle(command)
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
) -> JSONResponse:
    """Update a user."""
    command = UpdateUserCommand(
        user_id=user_id,
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name,
    )
    await handler.handle(command)

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
) -> JSONResponse:
    """Delete a user (soft delete)."""
    command = DeleteUserCommand(user_id=user_id)
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
