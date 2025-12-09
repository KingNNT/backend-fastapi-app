"""Log API controller - V1."""

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.core.application.commands.log import CreateLogCommand
from app.core.application.queries.log import (
    GetLogByIdQuery,
    ListLogsByUserQuery,
    ListLogsQuery,
)
from app.presentation.dependencies import (
    CreateLogHandlerDep,
    GetLogByIdHandlerDep,
    ListLogsByUserHandlerDep,
    ListLogsHandlerDep,
)
from app.presentation.dtos import (
    CreatedResponse,
    LogCreateRequest,
    LogListResponse,
    LogResponse,
    NotFoundResponse,
    SuccessResponse,
    ValidationErrorResponse,
)

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatedResponse[LogResponse],
    responses={
        422: {"model": ValidationErrorResponse, "description": "Validation error"},
    },
)
async def create_log(
    request: LogCreateRequest,
    handler: CreateLogHandlerDep,
) -> JSONResponse:
    """Create a new log entry."""
    command = CreateLogCommand(
        action=request.action,
        user_id=request.user_id,
        metadata=request.metadata,
    )
    log_id = await handler.handle(command)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Log created successfully",
            "data": {"id": log_id},
        },
    )


@router.get(
    "/",
    response_model=SuccessResponse[LogListResponse],
    summary="List Logs",
    description="Retrieve a paginated list of logs",
    responses={
        422: {
            "model": ValidationErrorResponse,
            "description": "Invalid query parameters",
        },
    },
)
async def list_logs(
    handler: ListLogsHandlerDep,
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of logs to return"
    ),
) -> JSONResponse:
    """List all logs with pagination."""
    query = ListLogsQuery(skip=skip, limit=limit)
    logs = await handler.handle(query)

    log_responses = [
        {
            "id": log.id,
            "action": log.action,
            "user_id": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "metadata": log.metadata,
        }
        for log in logs
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Logs retrieved successfully",
            "data": {
                "data": log_responses,
                "skip": skip,
                "limit": limit,
                "count": len(logs),
                "total": len(logs) + skip,
            },
        },
    )


@router.get(
    "/{log_id}",
    response_model=SuccessResponse[LogResponse],
    responses={
        404: {"model": NotFoundResponse, "description": "Log not found"},
    },
)
async def get_log(
    log_id: str,
    handler: GetLogByIdHandlerDep,
) -> JSONResponse:
    """Get a log by ID."""
    query = GetLogByIdQuery(log_id=log_id)
    log = await handler.handle(query)

    if log is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": f"Log with id '{log_id}' not found",
                "error_code": "LOG_NOT_FOUND",
                "data": None,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Log retrieved successfully",
            "data": {
                "id": log.id,
                "action": log.action,
                "user_id": log.user_id,
                "timestamp": log.timestamp.isoformat(),
                "metadata": log.metadata,
            },
        },
    )


@router.get(
    "/by-user/{user_id}",
    response_model=SuccessResponse[LogListResponse],
    summary="List Logs by User",
    description="Retrieve logs for a specific user",
)
async def list_logs_by_user(
    user_id: str,
    handler: ListLogsByUserHandlerDep,
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of logs to return"
    ),
) -> JSONResponse:
    """List logs for a specific user."""
    query = ListLogsByUserQuery(user_id=user_id, skip=skip, limit=limit)
    logs = await handler.handle(query)

    log_responses = [
        {
            "id": log.id,
            "action": log.action,
            "user_id": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "metadata": log.metadata,
        }
        for log in logs
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Logs retrieved successfully",
            "data": {
                "data": log_responses,
                "skip": skip,
                "limit": limit,
                "count": len(logs),
                "total": len(logs) + skip,
            },
        },
    )
