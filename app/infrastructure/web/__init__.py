"""Web infrastructure - FastAPI utilities."""

from app.infrastructure.web.exception_handlers import register_exception_handlers
from app.infrastructure.web.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.infrastructure.web.response import APIResponse

__all__ = [
    "register_exception_handlers",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "APIResponse",
]
