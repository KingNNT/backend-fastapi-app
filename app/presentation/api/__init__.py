"""Presentation layer — only system/health routes.

IAM and Audit BC routers are included directly in app/main.py from their own
BC presentation/api/__init__.py modules.
"""

from fastapi import APIRouter

from app.presentation.api import system

router = APIRouter()
router.include_router(system.router)
