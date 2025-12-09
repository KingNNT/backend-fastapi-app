"""
Application entry point with Clean Architecture.

This FastAPI application follows Clean Architecture + DDD + CQRS patterns:
- Domain Layer: Pure business logic (core/domain/)
- Application Layer: CQRS handlers (core/application/)
- Presentation Layer: API controllers (presentation/)
- Infrastructure Layer: Database implementations (infrastructure/)
"""

import logging.config

from fastapi import FastAPI

from app.infrastructure.configs import (
    get_app_config,
    get_app_version,
    get_log_config,
)
from app.infrastructure.setup import clean_architecture_lifespan
from app.infrastructure.web import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    register_exception_handlers,
)
from app.presentation.api import api_router

config = get_app_config()

# Configure global logging with dictConfig
logging.config.dictConfig(get_log_config(config.log_level))

app = FastAPI(
    title=config.name,
    version=get_app_version(),
    description=config.description,
    lifespan=clean_architecture_lifespan,
)

# Register exception handlers for domain exceptions
register_exception_handlers(app)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Include API routers
app.include_router(api_router)
