"""Application entry point - BC Modular Monolith.

Each Bounded Context exposes its own router via app.<bc>.presentation.api.
The composition root (this file) wires everything together.
"""

import logging.config

from fastapi import FastAPI

from app.audit.presentation.api import router as audit_router
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

logging.config.dictConfig(get_log_config(config.log_level))

app = FastAPI(
    title=config.name,
    version=get_app_version(),
    description=config.description,
    lifespan=app_lifespan,
)

register_exception_handlers(app)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(system_router)
app.include_router(iam_router, prefix="/v1")
app.include_router(audit_router, prefix="/v1")
