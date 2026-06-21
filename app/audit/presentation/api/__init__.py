"""Audit API router aggregator."""

from fastapi import APIRouter

from app.audit.presentation.api import log

router = APIRouter()
router.include_router(log.router)
