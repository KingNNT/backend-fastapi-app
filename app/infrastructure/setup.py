"""Infrastructure setup - initializes all dependencies for Clean Architecture."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.application.commands.handlers.log_handlers import CreateLogHandler
from app.core.domain.events.user_events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserUpdated,
)
from app.infrastructure.event_handlers import UserEventHandler
from app.infrastructure.messaging import InMemoryEventBus, SimplePasswordHasher
from app.infrastructure.persistence.mongodb.database import mongo_db_manager
from app.infrastructure.persistence.mongodb.repositories import (
    MongoLogReadModelRepository,
    MongoLogWriteRepository,
)
from app.infrastructure.persistence.postgresql.database import postgres_db_manager
from app.infrastructure.persistence.postgresql.repositories import (
    AssignmentRepository,
    PostgresPermissionReadModelRepository,
    PostgresPermissionReadRepository,
    PostgresPermissionWriteRepository,
    PostgresRoleReadModelRepository,
    PostgresRoleReadRepository,
    PostgresRoleWriteRepository,
    PostgresUserReadModelRepository,
    PostgresUserReadRepository,
    PostgresUserWriteRepository,
)
from app.presentation.dependencies import (
    set_event_bus,
    set_log_read_model_repository,
    set_log_repository,
    set_password_hasher,
    set_user_read_model_repository,
    set_user_repository,
)
from app.presentation.dependencies.repositories import (
    set_assignment_repository,
    set_permission_read_model_repository,
    set_permission_repository,
    set_role_read_model_repository,
    set_role_repository,
)

logger = logging.getLogger(__name__)


class CombinedUserRepository:
    """Combined repository that implements both read and write operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._write_repo = PostgresUserWriteRepository(session)
        self._read_repo = PostgresUserReadRepository(session)

    # Write operations
    async def save(self, aggregate):
        return await self._write_repo.save(aggregate)

    async def delete(self, aggregate):
        return await self._write_repo.delete(aggregate)

    async def exists_by_email(self, email):
        return await self._write_repo.exists_by_email(email)

    async def exists_by_username(self, username):
        return await self._write_repo.exists_by_username(username)

    # Read operations
    async def get_by_id(self, user_id):
        return await self._read_repo.get_by_id(user_id)

    async def get_by_email(self, email):
        return await self._read_repo.get_by_email(email)

    async def get_by_username(self, username):
        return await self._read_repo.get_by_username(username)

    async def list_all(self, skip=0, limit=100, include_deleted=False):
        return await self._read_repo.list_all(skip, limit, include_deleted)

    async def count(self, include_deleted=False):
        return await self._read_repo.count(include_deleted)


class CombinedRoleRepository:
    """Combined repository that implements both read and write operations for roles."""

    def __init__(self, session: AsyncSession) -> None:
        self._write_repo = PostgresRoleWriteRepository(session)
        self._read_repo = PostgresRoleReadRepository(session)

    # Write operations
    async def save(self, aggregate):
        return await self._write_repo.save(aggregate)

    async def delete(self, aggregate):
        return await self._write_repo.delete(aggregate)

    async def exists_by_name(self, name):
        return await self._write_repo.exists_by_name(name)

    # Read operations
    async def get_by_id(self, role_id):
        return await self._read_repo.get_by_id(role_id)

    async def get_by_name(self, name):
        return await self._read_repo.get_by_name(name)

    async def list_all(self, skip=0, limit=100, include_deleted=False):
        return await self._read_repo.list_all(skip, limit, include_deleted)

    async def count(self, include_deleted=False):
        return await self._read_repo.count(include_deleted)


class CombinedPermissionRepository:
    """Combined repo that implements both read and write operations for permissions."""

    def __init__(self, session: AsyncSession) -> None:
        self._write_repo = PostgresPermissionWriteRepository(session)
        self._read_repo = PostgresPermissionReadRepository(session)

    # Write operations
    async def save(self, aggregate):
        return await self._write_repo.save(aggregate)

    async def delete(self, aggregate):
        return await self._write_repo.delete(aggregate)

    async def exists_by_name(self, name):
        return await self._write_repo.exists_by_name(name)

    # Read operations
    async def get_by_id(self, permission_id):
        return await self._read_repo.get_by_id(permission_id)

    async def get_by_name(self, name):
        return await self._read_repo.get_by_name(name)

    async def list_all(self, skip=0, limit=100, include_deleted=False):
        return await self._read_repo.list_all(skip, limit, include_deleted)

    async def count(self, include_deleted=False):
        return await self._read_repo.count(include_deleted)


def setup_dependencies(session: AsyncSession) -> None:
    """Set up all dependency injection bindings."""
    # Create user repositories
    combined_user_repo = CombinedUserRepository(session)
    user_read_model_repo = PostgresUserReadModelRepository(session)

    # Create role repositories
    combined_role_repo = CombinedRoleRepository(session)
    role_read_model_repo = PostgresRoleReadModelRepository(session)

    # Create permission repositories
    combined_permission_repo = CombinedPermissionRepository(session)
    permission_read_model_repo = PostgresPermissionReadModelRepository(session)

    # Create assignment repository
    assignment_repo = AssignmentRepository(session)

    # Create log repositories
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

    # Set user dependency injection bindings
    set_user_repository(combined_user_repo)
    set_user_read_model_repository(user_read_model_repo)

    # Set role dependency injection bindings
    set_role_repository(combined_role_repo)
    set_role_read_model_repository(role_read_model_repo)

    # Set permission dependency injection bindings
    set_permission_repository(combined_permission_repo)
    set_permission_read_model_repository(permission_read_model_repo)

    # Set assignment dependency injection bindings
    set_assignment_repository(assignment_repo)

    # Set log dependency injection bindings
    set_log_repository(log_write_repo)
    set_log_read_model_repository(log_read_model_repo)

    # Set infrastructure services
    set_event_bus(event_bus)
    set_password_hasher(password_hasher)

    logger.info("Dependencies configured successfully")


@asynccontextmanager
async def clean_architecture_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager for Clean Architecture.

    Manages both PostgreSQL and MongoDB connections and sets up
    all dependency injection bindings.
    """
    # Startup
    logger.info("Starting application with Clean Architecture...")

    # Initialize databases using centralized managers
    await postgres_db_manager.connect()
    await mongo_db_manager.connect()

    if postgres_db_manager.session_maker is None:
        raise RuntimeError("PostgreSQL session maker is not initialized")

    # Create a session for the application lifetime
    # Note: In a real app, you'd want request-scoped sessions
    async with postgres_db_manager.session_maker() as session:
        setup_dependencies(session)

        yield  # Application runs

    # Shutdown
    await postgres_db_manager.close()
    await mongo_db_manager.close()

    logger.info("Application shutdown complete")
