"""API routers."""

from fastapi import APIRouter

from app.presentation.api import system
from app.presentation.api.v1 import v1_router

api_router = APIRouter()

# Include system routes (no version prefix)
api_router.include_router(system.router)

# Include versioned API routes
api_router.include_router(v1_router)
