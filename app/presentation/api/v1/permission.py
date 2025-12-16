"""Permission API controller - V1."""

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.core.application.commands.permission import (
    CreatePermissionCommand,
    DeletePermissionCommand,
    UpdatePermissionCommand,
)
from app.core.application.queries.permission import (
    GetPermissionByIdQuery,
    GetPermissionByNameQuery,
    ListPermissionsQuery,
)
from app.core.domain.exceptions.permission import PermissionNotFound
from app.presentation.dependencies.handlers import (
    CreatePermissionHandlerDep,
    DeletePermissionHandlerDep,
    GetPermissionByIdHandlerDep,
    GetPermissionByNameHandlerDep,
    ListPermissionsHandlerDep,
    UpdatePermissionHandlerDep,
)
from app.presentation.dtos import (
    BadRequestResponse,
    ConflictResponse,
    CreatedResponse,
    NotFoundResponse,
    PermissionCreateRequest,
    PermissionListResponse,
    PermissionResponse,
    PermissionUpdateRequest,
    SuccessResponse,
    ValidationErrorResponse,
)

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatedResponse[PermissionResponse],
    responses={
        400: {"model": BadRequestResponse, "description": "Invalid input data"},
        409: {"model": ConflictResponse, "description": "Permission already exists"},
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
    },
)
async def create_permission(
    request: PermissionCreateRequest,
    handler: CreatePermissionHandlerDep,
) -> JSONResponse:
    """Create a new permission."""
    command = CreatePermissionCommand(
        name=request.name,
        description=request.description,
    )
    permission_id = await handler.handle(command)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Permission created successfully",
            "data": {"id": permission_id},
        },
    )


@router.get(
    "/",
    response_model=SuccessResponse[PermissionListResponse],
    summary="List Permissions",
    description="Retrieve a paginated list of permissions",
    responses={
        422: {
            "model": ValidationErrorResponse,
            "description": "Invalid query parameters",
        },
    },
)
async def list_permissions(
    handler: ListPermissionsHandlerDep,
    skip: int = Query(0, ge=0, description="Number of permissions to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of permissions to return"
    ),
) -> JSONResponse:
    """List all permissions with pagination."""
    query = ListPermissionsQuery(skip=skip, limit=limit)
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
            "message": "Permissions retrieved successfully",
            "data": {
                "data": permission_responses,
                "skip": skip,
                "limit": limit,
                "count": len(permissions),
                "total": len(permissions) + skip,
            },
        },
    )


@router.get(
    "/{permission_id}",
    response_model=SuccessResponse[PermissionResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "Permission not found"},
    },
)
async def get_permission(
    permission_id: str,
    handler: GetPermissionByIdHandlerDep,
) -> JSONResponse:
    """Get a permission by ID."""
    query = GetPermissionByIdQuery(permission_id=permission_id)
    permission = await handler.handle(query)

    if permission is None:
        raise PermissionNotFound(permission_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Permission retrieved successfully",
            "data": {
                "id": permission.id,
                "name": permission.name,
                "description": permission.description,
                "created_at": permission.created_at.isoformat(),
                "updated_at": permission.updated_at.isoformat(),
            },
        },
    )


@router.get(
    "/by-name/{name}",
    response_model=SuccessResponse[PermissionResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "Permission not found"},
    },
)
async def get_permission_by_name(
    name: str,
    handler: GetPermissionByNameHandlerDep,
) -> JSONResponse:
    """Get a permission by name."""
    query = GetPermissionByNameQuery(name=name)
    permission = await handler.handle(query)

    if permission is None:
        raise PermissionNotFound(message=f"Permission with name '{name}' not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Permission retrieved successfully",
            "data": {
                "id": permission.id,
                "name": permission.name,
                "description": permission.description,
                "created_at": permission.created_at.isoformat(),
                "updated_at": permission.updated_at.isoformat(),
            },
        },
    )


@router.put(
    "/{permission_id}",
    response_model=SuccessResponse[PermissionResponse],
    responses={
        400: {"model": BadRequestResponse, "description": "Invalid input data"},
        404: {"model": NotFoundResponse, "description": "Permission not found"},
        409: {
            "model": ConflictResponse,
            "description": "Permission name already exists",
        },
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
    },
)
async def update_permission(
    permission_id: str,
    request: PermissionUpdateRequest,
    handler: UpdatePermissionHandlerDep,
) -> JSONResponse:
    """Update a permission."""
    command = UpdatePermissionCommand(
        permission_id=permission_id,
        name=request.name,
        description=request.description,
    )
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Permission updated successfully",
            "data": {"id": permission_id},
        },
    )


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": NotFoundResponse, "description": "Permission not found"},
    },
)
async def delete_permission(
    permission_id: str,
    handler: DeletePermissionHandlerDep,
) -> JSONResponse:
    """Delete a permission (soft delete)."""
    command = DeletePermissionCommand(permission_id=permission_id)
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
