"""Application entry point - BC Modular Monolith.

Each Bounded Context exposes its own router via app.<bc>.presentation.api.
The composition root (this file) wires everything together.
"""

import logging.config

from fastapi import FastAPI

from app.iam.presentation.api import router as iam_router
from app.infrastructure.setup import app_lifespan
from app.platform.configs import (
    get_app_config,
    get_app_version,
    get_log_config,
)
from app.platform.web import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    register_exception_handlers,
)
from app.presentation.api import router as system_router

config = get_app_config()

# Configure global logging with dictConfig
logging.config.dictConfig(get_log_config(config.log_level))

app = FastAPI(
    title=config.name,
    version=get_app_version(),
    description=config.description,
    lifespan=app_lifespan,
)

# Register exception handlers for domain exceptions
register_exception_handlers(app)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Include BC routers
app.include_router(system_router)  # /health-check, /version
app.include_router(iam_router, prefix="/v1")  # /v1/users, /v1/roles, etc.
# TODO Phase 4: app.include_router(audit_router, prefix="/v1")  # /v1/logs
