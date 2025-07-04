"""HTTP middleware for request/response processing.

This module contains middleware functions for cross-cutting concerns
like logging, authentication, CORS, rate limiting, etc.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        start_time = time.time()

        # Log request
        print(f"🔵 {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        print(f"🟢 {response.status_code} - {process_time:.3f}s")

        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


# Example usage in main.py:
# app.add_middleware(RequestLoggingMiddleware)
# app.add_middleware(SecurityHeadersMiddleware)
