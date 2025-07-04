from fastapi import FastAPI

from app.configs.app import get_app_config
from app.configs.database import database_lifespan
from app.configs.version import get_app_version
from app.api.exception_handlers import register_exception_handlers
from app.routers import system
from app.routers.v1 import user as user_v1

config = get_app_config()

app = FastAPI(
    title=config.name,
    version=get_app_version(),
    description=config.description,
    lifespan=database_lifespan,
)

# Register exception handlers
register_exception_handlers(app)

app.include_router(system.router)
app.include_router(user_v1.router, prefix="/v1")
