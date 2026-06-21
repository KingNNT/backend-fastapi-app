"""Web infrastructure - FastAPI utilities."""

from app.platform.web.exception_handlers import register_exception_handlers
from app.platform.web.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.platform.web.response import APIResponse

__all__ = [
    "register_exception_handlers",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "APIResponse",
]
