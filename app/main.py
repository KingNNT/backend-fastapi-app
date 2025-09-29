import logging.config
from fastapi import FastAPI

from app.configs import (
    get_app_config,
    database_lifespan,
    get_app_version,
    get_log_config,
)
from app.dependencies import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.internal.exceptions import register_exception_handlers
from app.routers import system
from app.routers.v1 import v1_router

config = get_app_config()

# Configure global logging with dictConfig
logging.config.dictConfig(get_log_config(config.log_level))

app = FastAPI(
    title=config.name,
    version=get_app_version(),
    description=config.description,
    lifespan=database_lifespan,
)

# Register exception handlers
register_exception_handlers(app)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(system.router)
app.include_router(v1_router)
