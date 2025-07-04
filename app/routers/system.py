from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.response import APIResponse
from app.configs.version import get_version_info
from app.internal.dtos import SystemStatusResponse
from app.internal.services.system import SystemService

router = APIRouter(tags=["System"])


@router.get("/health-check")
async def health_check(
    system_service: SystemService = Depends(SystemService),
) -> JSONResponse:
    r = await system_service.health_check()
    response = SystemStatusResponse(alive=r)
    return APIResponse.success_response(
        data=response.model_dump(), message="Health check completed"
    )


@router.get("/version")
async def get_version() -> JSONResponse:
    version_info = get_version_info()
    return APIResponse.success_response(
        data=version_info.model_dump(), message="Version information retrieved"
    )
