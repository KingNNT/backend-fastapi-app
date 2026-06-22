"""Role API controller - V1."""

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.iam.application.commands.assignment import (
    AssignPermissionToRoleCommand,
    RemovePermissionFromRoleCommand,
)
from app.iam.application.commands.role import (
    CreateRoleCommand,
    DeleteRoleCommand,
    UpdateRoleCommand,
)
from app.iam.application.queries.assignment import GetRolePermissionsQuery
from app.iam.application.queries.role import (
    GetRoleByIdQuery,
    GetRoleByNameQuery,
    ListRolesQuery,
)
from app.iam.domain.role.exceptions import RoleNotFound
from app.iam.presentation.dependencies.handlers import (
    AssignPermissionToRoleHandlerDep,
    CreateRoleHandlerDep,
    DeleteRoleHandlerDep,
    GetRoleByIdHandlerDep,
    GetRoleByNameHandlerDep,
    GetRolePermissionsHandlerDep,
    ListRolesHandlerDep,
    RemovePermissionFromRoleHandlerDep,
    UpdateRoleHandlerDep,
)
from app.iam.presentation.dependencies.repositories import IamUnitOfWorkDep
from app.iam.presentation.dtos import (
    AssignRolePermissionRequest,
    RoleCreateRequest,
    RoleListResponse,
    RoleResponse,
    RoleUpdateRequest,
)
from app.platform.web.response_dtos import (
    BadRequestResponse,
    ConflictResponse,
    CreatedResponse,
    NotFoundResponse,
    SuccessResponse,
    ValidationErrorResponse,
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatedResponse[RoleResponse],
    responses={
        400: {"model": BadRequestResponse, "description": "Invalid input data"},
        409: {"model": ConflictResponse, "description": "Role already exists"},
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
    },
)
async def create_role(
    request: RoleCreateRequest,
    handler: CreateRoleHandlerDep,
    uow: IamUnitOfWorkDep,
) -> JSONResponse:
    """Create a new role."""
    command = CreateRoleCommand(
        name=request.name,
        description=request.description,
    )
    role_id = await handler.handle(command, uow)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Role created successfully",
            "data": {"id": role_id},
        },
    )


@router.get(
    "/",
    response_model=SuccessResponse[RoleListResponse],
    summary="List Roles",
    description="Retrieve a paginated list of roles",
    responses={
        422: {
            "model": ValidationErrorResponse,
            "description": "Invalid query parameters",
        },
    },
)
async def list_roles(
    handler: ListRolesHandlerDep,
    skip: int = Query(0, ge=0, description="Number of roles to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of roles to return"
    ),
) -> JSONResponse:
    """List all roles with pagination."""
    query = ListRolesQuery(skip=skip, limit=limit)
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
            "message": "Roles retrieved successfully",
            "data": {
                "data": role_responses,
                "skip": skip,
                "limit": limit,
                "count": len(roles),
                "total": len(roles) + skip,
            },
        },
    )


@router.get(
    "/{role_id}",
    response_model=SuccessResponse[RoleResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "Role not found"},
    },
)
async def get_role(
    role_id: str,
    handler: GetRoleByIdHandlerDep,
) -> JSONResponse:
    """Get a role by ID."""
    query = GetRoleByIdQuery(role_id=role_id)
    role = await handler.handle(query)

    if role is None:
        raise RoleNotFound(role_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Role retrieved successfully",
            "data": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat(),
            },
        },
    )


@router.get(
    "/by-name/{name}",
    response_model=SuccessResponse[RoleResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "Role not found"},
    },
)
async def get_role_by_name(
    name: str,
    handler: GetRoleByNameHandlerDep,
) -> JSONResponse:
    """Get a role by name."""
    query = GetRoleByNameQuery(name=name)
    role = await handler.handle(query)

    if role is None:
        raise RoleNotFound(message=f"Role with name '{name}' not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Role retrieved successfully",
            "data": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat(),
            },
        },
    )


@router.put(
    "/{role_id}",
    response_model=SuccessResponse[RoleResponse],
    responses={
        400: {"model": BadRequestResponse, "description": "Invalid input data"},
        404: {"model": NotFoundResponse, "description": "Role not found"},
        409: {"model": ConflictResponse, "description": "Role name already exists"},
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
    },
)
async def update_role(
    role_id: str,
    request: RoleUpdateRequest,
    handler: UpdateRoleHandlerDep,
    uow: IamUnitOfWorkDep,
) -> JSONResponse:
    """Update a role."""
    command = UpdateRoleCommand(
        role_id=role_id,
        name=request.name,
        description=request.description,
    )
    await handler.handle(command, uow)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Role updated successfully",
            "data": {"id": role_id},
        },
    )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": NotFoundResponse, "description": "Role not found"},
    },
)
async def delete_role(
    role_id: str,
    handler: DeleteRoleHandlerDep,
    uow: IamUnitOfWorkDep,
) -> JSONResponse:
    """Delete a role (soft delete)."""
    command = DeleteRoleCommand(role_id=role_id)
    await handler.handle(command, uow)

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )


# Role-Permission assignment endpoints
@router.get(
    "/{role_id}/permissions",
    response_model=SuccessResponse[list],
    responses={
        404: {"model": NotFoundResponse, "description": "Role not found"},
    },
)
async def get_role_permissions(
    role_id: str,
    handler: GetRolePermissionsHandlerDep,
) -> JSONResponse:
    """Get all permissions assigned to a role."""
    query = GetRolePermissionsQuery(role_id=role_id)
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
            "message": "Role permissions retrieved successfully",
            "data": permission_responses,
        },
    )


@router.post(
    "/{role_id}/permissions",
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": NotFoundResponse, "description": "Role or permission not found"},
        409: {"model": ConflictResponse, "description": "Permission already assigned"},
    },
)
async def assign_permission_to_role(
    role_id: str,
    request: AssignRolePermissionRequest,
    handler: AssignPermissionToRoleHandlerDep,
) -> JSONResponse:
    """Assign a permission to a role."""
    command = AssignPermissionToRoleCommand(
        role_id=role_id,
        permission_id=request.permission_id,
    )
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Permission assigned to role successfully",
            "data": {
                "role_id": role_id,
                "permission_id": request.permission_id,
            },
        },
    )


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": NotFoundResponse, "description": "Assignment not found"},
    },
)
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    handler: RemovePermissionFromRoleHandlerDep,
) -> JSONResponse:
    """Remove a permission from a role."""
    command = RemovePermissionFromRoleCommand(
        role_id=role_id,
        permission_id=permission_id,
    )
    await handler.handle(command)

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None,
    )
