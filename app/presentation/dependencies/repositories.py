"""Dependency injection for repositories."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.application.queries.handlers.assignment_handlers import (
    IAssignmentQueryRepository,
    IPermissionReadModelRepository,
    IRoleReadModelRepository,
)
from app.core.application.queries.handlers.log_handlers import ILogReadModelRepository
from app.core.application.queries.handlers.user_handlers import IUserReadModelRepository
from app.core.domain.repositories.log import ILogWriteRepository
from app.core.domain.repositories.permission import IPermissionRepository
from app.core.domain.repositories.role import IRoleRepository
from app.core.domain.repositories.user import IUserRepository
from app.infrastructure.persistence.postgresql.database import get_postgres_session
from app.infrastructure.persistence.postgresql.repositories import (
    AssignmentRepository,
    CombinedPermissionRepository,
    CombinedRoleRepository,
    CombinedUserRepository,
    PostgresPermissionReadModelRepository,
    PostgresRoleReadModelRepository,
    PostgresUserReadModelRepository,
)

# =============================================================================
# PostgreSQL Repositories - Request-scoped (new session per request)
# =============================================================================


async def get_user_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IUserRepository, None]:
    """Get user repository with request-scoped session."""
    yield CombinedUserRepository(session)


async def get_user_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IUserReadModelRepository, None]:
    """Get user read model repository with request-scoped session."""
    yield PostgresUserReadModelRepository(session)


async def get_role_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IRoleRepository, None]:
    """Get role repository with request-scoped session."""
    yield CombinedRoleRepository(session)


async def get_role_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IRoleReadModelRepository, None]:
    """Get role read model repository with request-scoped session."""
    yield PostgresRoleReadModelRepository(session)


async def get_permission_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IPermissionRepository, None]:
    """Get permission repository with request-scoped session."""
    yield CombinedPermissionRepository(session)


async def get_permission_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IPermissionReadModelRepository, None]:
    """Get permission read model repository with request-scoped session."""
    yield PostgresPermissionReadModelRepository(session)


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
