from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_user_service
from app.api.response import APIResponse
from app.internal.dtos.user import UserCreate, UserUpdate
from app.internal.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    user = await user_service.create_user(user_data)
    return APIResponse.success_response(
        data=user,
        message="User created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of users to return"
    ),
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    users = await user_service.get_users(skip=skip, limit=limit)
    return APIResponse.success_response(
        data=users,
        message="Users retrieved successfully",
        meta={"skip": skip, "limit": limit, "count": len(users)},
    )


@router.get("/{user_id}")
async def get_user(
    user_id: PydanticObjectId, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    user = await user_service.get_user(user_id)
    return APIResponse.success_response(
        data=user, message="User retrieved successfully"
    )


@router.put("/{user_id}")
async def update_user(
    user_id: PydanticObjectId,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    user = await user_service.update_user(user_id, user_data)
    return APIResponse.success_response(data=user, message="User updated successfully")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: PydanticObjectId, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    await user_service.delete_user(user_id)
    return APIResponse.success_response(
        data=None,
        message="User deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.get("/by-email/{email}")
async def get_user_by_email(
    email: str, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    user = await user_service.get_user_by_email(email)
    return APIResponse.success_response(
        data=user, message="User retrieved successfully"
    )


@router.get("/by-username/{username}")
async def get_user_by_username(
    username: str, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    user = await user_service.get_user_by_username(username)
    return APIResponse.success_response(
        data=user, message="User retrieved successfully"
    )
