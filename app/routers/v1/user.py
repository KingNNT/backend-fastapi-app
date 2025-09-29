from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.internal.services import get_user_service
from app.utils.response import APIResponse
from app.internal.dtos import (
    UserCreate,
    UserUpdate,
    UserResponse,
    SuccessResponse,
    CreatedResponse,
    NotFoundResponse,
    ValidationErrorResponse,
    ConflictResponse,
    BadRequestResponse,
    Pagination,
)
from app.internal.services import UserService

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
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    user = await user_service.create_user(user_data)
    return APIResponse.success_response(
        data=user.model_dump(mode="json"),
        message="User created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/",
    response_model=Pagination[UserResponse],
    summary="List Users",
    description="Retrieve a paginated list of users with optional filtering",
    responses={
        422: {
            "model": ValidationErrorResponse,
            "description": "Invalid query parameters",
        },
    },
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
    email: str | None = Query(None, description="Filter by email address"),
    username: str | None = Query(None, description="Filter by username"),
    user_service: UserService = Depends(get_user_service),
):
    users = await user_service.get_users(
        skip=skip, limit=limit, email=email, username=username
    )

    # For now, we'll use the count as total (in a real app, you'd get the actual total count)
    total = len(users) + skip  # Simple approximation

    response = Pagination(
        data=users, skip=skip, limit=limit, count=len(users), total=total
    ).model_dump(mode="json")

    return APIResponse.success_response(
        data=response, message="Users retrieved successfully"
    )


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def get_user(
    user_id: PydanticObjectId, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    user = await user_service.get_user(user_id)
    return APIResponse.success_response(
        data=user.model_dump(mode="json"), message="User retrieved successfully"
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
    user_id: PydanticObjectId,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    user = await user_service.update_user(user_id, user_data)
    return APIResponse.success_response(
        data=user.model_dump(mode="json"), message="User updated successfully"
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": NotFoundResponse, "description": "User not found"},
    },
)
async def delete_user(
    user_id: PydanticObjectId, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    await user_service.delete_user(user_id)
    return APIResponse.success_response(
        data=None,
        message="User deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
    )
