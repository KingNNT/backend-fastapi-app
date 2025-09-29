from fastapi import APIRouter

from app.routers.v1 import user

# Create the main v1 router with /v1 prefix
v1_router = APIRouter(prefix="/v1")

# Include all v1 sub-routers
v1_router.include_router(user.router)

__all__ = ["v1_router"]
