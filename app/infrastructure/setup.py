"""Application composition root - initializes all dependencies and wires BCs."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.audit.application.handlers import CreateLogHandler
from app.audit.infrastructure.event_handlers import AuditUserEventTranslator
from app.audit.infrastructure.persistence.mongodb.repositories import (
    MongoLogReadModelRepository,
    MongoLogWriteRepository,
)
from app.audit.presentation.dependencies.repositories import (
    set_log_read_model_repository,
    set_log_repository,
)
from app.iam.domain.user.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserUpdated,
)
from app.iam.infrastructure.messaging.password_hasher import SimplePasswordHasher
from app.platform.messaging.event_bus import InMemoryEventBus
from app.platform.messaging.services import (
    set_event_bus,
    set_password_hasher,
)
from app.platform.persistence.mongodb.database import mongo_db_manager
from app.platform.persistence.postgresql.database import postgres_db_manager

logger = logging.getLogger(__name__)


def setup_app_services() -> None:
    """Set up app-scoped services (event bus, password hasher, MongoDB repos)."""
    log_write_repo = MongoLogWriteRepository()
    log_read_model_repo = MongoLogReadModelRepository()

    event_bus = InMemoryEventBus()
    password_hasher = SimplePasswordHasher()

    log_handler = CreateLogHandler(
        repository=log_write_repo,
        event_bus=event_bus,
    )

    # Cross-BC wiring: audit subscribes to IAM events
    audit_translator = AuditUserEventTranslator(create_log_handler=log_handler)
    event_bus.subscribe(UserCreated, audit_translator.on_user_created)
    event_bus.subscribe(UserUpdated, audit_translator.on_user_updated)
    event_bus.subscribe(UserDeleted, audit_translator.on_user_deleted)
    event_bus.subscribe(UserDeactivated, audit_translator.on_user_deactivated)
    event_bus.subscribe(UserActivated, audit_translator.on_user_activated)

    set_log_repository(log_write_repo)
    set_log_read_model_repository(log_read_model_repo)
    set_event_bus(event_bus)
    set_password_hasher(password_hasher)

    logger.info("App-scoped services configured successfully")


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    logger.info("Starting application...")

    await postgres_db_manager.connect()
    await mongo_db_manager.connect()

    setup_app_services()

    yield

    await postgres_db_manager.close()
    await mongo_db_manager.close()

    logger.info("Application shutdown complete")
