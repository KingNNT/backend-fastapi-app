"""System API controller."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.infrastructure.configs import get_app_config

router = APIRouter(tags=["System"])


@router.get("/health-check")
async def health_check() -> JSONResponse:
    """Check application health status."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Application is healthy",
            "data": {
                "status": "healthy",
                "message": "All systems operational",
            },
        },
    )


@router.get("/version")
async def version() -> JSONResponse:
    """Get application version information."""
    config = get_app_config()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Version information retrieved",
            "data": {
                "name": config.APP_NAME,
                "version": config.APP_VERSION,
                "environment": config.ENVIRONMENT,
            },
        },
    )
