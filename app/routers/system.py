from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.utils.response import APIResponse
from app.configs.version import get_version_info
from app.internal.dtos import (
    SystemStatusResponse,
    VersionInformationResponse,
    SuccessResponse,
)
from app.internal.services.system import SystemService

router = APIRouter(tags=["System"])


@router.get(
    "/health-check",
    response_model=SuccessResponse[SystemStatusResponse],
    summary="Health check endpoint",
    description="Check the health status of the application and its dependencies",
)
async def health_check(
    system_service: SystemService = Depends(SystemService),
) -> JSONResponse:
    r = await system_service.health_check()
    response = SystemStatusResponse(alive=r).model_dump(mode="json")
    return APIResponse.success_response(data=response, message="Health check completed")


@router.get(
    "/version",
    response_model=SuccessResponse[VersionInformationResponse],
    summary="Version information",
    description="Get application version and build information",
)
async def get_version() -> JSONResponse:
    version_info = get_version_info()
    return APIResponse.success_response(
        data=version_info.model_dump(), message="Version information retrieved"
    )
