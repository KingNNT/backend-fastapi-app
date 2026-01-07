"""Dependency injection for repositories."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.application.interfaces import IUnitOfWork
from app.core.application.interfaces.event_bus import IEventBus
from app.core.application.queries.handlers.assignment_handlers import (
    IAssignmentQueryRepository,
    IPermissionReadModelRepository,
    IRoleReadModelRepository,
)
from app.core.application.queries.handlers.log_handlers import ILogReadModelRepository
from app.core.application.queries.handlers.user_handlers import IUserReadModelRepository
from app.core.domain.repositories.log import ILogWriteRepository
from app.core.domain.repositories.permission import (
    IPermissionReadRepository,
    IPermissionWriteRepository,
)
from app.core.domain.repositories.role import (
    IRoleReadRepository,
    IRoleWriteRepository,
)
from app.core.domain.repositories.user import (
    IUserReadRepository,
    IUserWriteRepository,
)
from app.infrastructure.persistence.postgresql.database import (
    get_postgres_session,
    postgres_db_manager,
)
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
from app.infrastructure.persistence.postgresql.unit_of_work import PostgresUnitOfWork
from app.presentation.dependencies.services import get_event_bus

# =============================================================================
# PostgreSQL Repositories - Request-scoped (new session per request)
# =============================================================================
# Note: FastAPI caches Depends() within a request, so all repositories
# using Depends(get_postgres_session) will share the same session instance.
# This ensures transaction consistency across read and write operations.
# =============================================================================


# -----------------------------------------------------------------------------
# Unit of Work (Request-scoped with auto-commit)
# -----------------------------------------------------------------------------
async def get_unit_of_work(
    event_bus: IEventBus = Depends(get_event_bus),
) -> AsyncGenerator[IUnitOfWork, None]:
    """Get request-scoped Unit of Work with auto-commit.

    The Unit of Work:
    - Creates a new database session for each request
    - Contains lazy-initialized repositories (users, roles, permissions)
    - Auto-commits on successful request completion
    - Auto-rollbacks on exception
    - Publishes domain events AFTER successful commit

    Usage in controllers:
        @router.post("/")
        async def create_user(
            request: UserCreateRequest,
            handler: CreateUserHandlerDep,
            uow: UnitOfWorkDep,
        ):
            user_id = await handler.handle(command, uow)
            # Auto-commits when request ends
    """
    if postgres_db_manager.session_maker is None:
        raise RuntimeError(
            "Database is not connected. Call postgres_db_manager.connect() first."
        )

    uow = PostgresUnitOfWork(
        session_factory=postgres_db_manager.session_maker,
        event_bus=event_bus,
    )

    async with uow:  # Auto-commits on success, rollbacks on exception
        yield uow


# Type alias for dependency injection
UnitOfWorkDep = Annotated[IUnitOfWork, Depends(get_unit_of_work)]


# -----------------------------------------------------------------------------
# User Repositories
# -----------------------------------------------------------------------------
async def get_user_write_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IUserWriteRepository, None]:
    """Get user write repository with request-scoped session."""
    yield PostgresUserWriteRepository(session)


async def get_user_read_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IUserReadRepository, None]:
    """Get user read repository with request-scoped session."""
    yield PostgresUserReadRepository(session)


async def get_user_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IUserReadModelRepository, None]:
    """Get user read model repository with request-scoped session."""
    yield PostgresUserReadModelRepository(session)


# -----------------------------------------------------------------------------
# Role Repositories
# -----------------------------------------------------------------------------
async def get_role_write_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IRoleWriteRepository, None]:
    """Get role write repository with request-scoped session."""
    yield PostgresRoleWriteRepository(session)


async def get_role_read_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IRoleReadRepository, None]:
    """Get role read repository with request-scoped session."""
    yield PostgresRoleReadRepository(session)


async def get_role_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IRoleReadModelRepository, None]:
    """Get role read model repository with request-scoped session."""
    yield PostgresRoleReadModelRepository(session)


# -----------------------------------------------------------------------------
# Permission Repositories
# -----------------------------------------------------------------------------
async def get_permission_write_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IPermissionWriteRepository, None]:
    """Get permission write repository with request-scoped session."""
    yield PostgresPermissionWriteRepository(session)


async def get_permission_read_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IPermissionReadRepository, None]:
    """Get permission read repository with request-scoped session."""
    yield PostgresPermissionReadRepository(session)


async def get_permission_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IPermissionReadModelRepository, None]:
    """Get permission read model repository with request-scoped session."""
    yield PostgresPermissionReadModelRepository(session)


# -----------------------------------------------------------------------------
# Assignment Repository
# -----------------------------------------------------------------------------
async def get_assignment_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IAssignmentQueryRepository, None]:
    """Get assignment repository with request-scoped session."""
    yield AssignmentRepository(session)


# =============================================================================
# MongoDB Repositories - App-scoped (no session concerns)
# =============================================================================

_log_repository: ILogWriteRepository | None = None
_log_read_model_repository: ILogReadModelRepository | None = None


def set_log_repository(repo: ILogWriteRepository) -> None:
    """Set the log repository implementation."""
    global _log_repository
    _log_repository = repo


def set_log_read_model_repository(repo: ILogReadModelRepository) -> None:
    """Set the log read model repository implementation."""
    global _log_read_model_repository
    _log_read_model_repository = repo


def get_log_repository() -> ILogWriteRepository:
    """Get the log repository instance."""
    if _log_repository is None:
        raise RuntimeError("Log repository not initialized")
    return _log_repository


def get_log_read_model_repository() -> ILogReadModelRepository:
    """Get the log read model repository instance."""
    if _log_read_model_repository is None:
        raise RuntimeError("Log read model repository not initialized")
    return _log_read_model_repository
