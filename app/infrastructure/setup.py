"""Application composition root - initializes all dependencies and wires BCs."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.application.commands.handlers.log_handlers import CreateLogHandler
from app.iam.domain.user.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserUpdated,
)
from app.iam.infrastructure.messaging.password_hasher import SimplePasswordHasher
from app.infrastructure.event_handlers import UserEventHandler
from app.infrastructure.persistence.mongodb.repositories import (
    MongoLogReadModelRepository,
    MongoLogWriteRepository,
)
from app.platform.messaging.event_bus import InMemoryEventBus
from app.platform.messaging.services import (
    set_event_bus,
    set_password_hasher,
)
from app.platform.persistence.mongodb.database import mongo_db_manager
from app.platform.persistence.postgresql.database import postgres_db_manager
from app.presentation.dependencies.repositories import (
    set_log_read_model_repository,
    set_log_repository,
)

logger = logging.getLogger(__name__)


def setup_app_services() -> None:
    """Set up app-scoped services (event bus, password hasher, MongoDB repos)."""
    # Create MongoDB log repositories (app-scoped, no session concerns)
    log_write_repo = MongoLogWriteRepository()
    log_read_model_repo = MongoLogReadModelRepository()

    # Create infrastructure services
    event_bus = InMemoryEventBus()
    password_hasher = SimplePasswordHasher()

    # Set up event handlers
    log_handler = CreateLogHandler(
        repository=log_write_repo,
        event_bus=event_bus,
    )
    user_event_handler = UserEventHandler(create_log_handler=log_handler)

    # Subscribe event handlers
    event_bus.subscribe(UserCreated, user_event_handler.on_user_created)
    event_bus.subscribe(UserUpdated, user_event_handler.on_user_updated)
    event_bus.subscribe(UserDeleted, user_event_handler.on_user_deleted)
    event_bus.subscribe(UserDeactivated, user_event_handler.on_user_deactivated)
    event_bus.subscribe(UserActivated, user_event_handler.on_user_activated)

    # Set MongoDB repository bindings
    set_log_repository(log_write_repo)
    set_log_read_model_repository(log_read_model_repo)

    # Set infrastructure service bindings (global state in platform/messaging)
    set_event_bus(event_bus)
    set_password_hasher(password_hasher)

    logger.info("App-scoped services configured successfully")


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    logger.info("Starting application...")

    # Initialize database connections
    await postgres_db_manager.connect()
    await mongo_db_manager.connect()

    # Set up app-scoped services
    setup_app_services()

    yield  # Application runs

    # Shutdown
    await postgres_db_manager.close()
    await mongo_db_manager.close()

    logger.info("Application shutdown complete")
