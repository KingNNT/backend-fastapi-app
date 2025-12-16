"""V1 API router aggregation."""

from fastapi import APIRouter

from app.presentation.api.v1 import log, permission, role, user

v1_router = APIRouter(prefix="/v1")

# Include all v1 routers
v1_router.include_router(user.router)
v1_router.include_router(log.router)
v1_router.include_router(role.router)
v1_router.include_router(permission.router)
