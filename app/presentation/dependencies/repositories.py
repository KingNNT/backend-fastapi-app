"""Presentation-layer dependency providers for Log BC only.

IAM-specific dependencies (UoW, read model repos, password hasher) live in
app.iam.presentation.dependencies.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.application.queries.handlers.log_handlers import (
    ILogReadModelRepository,
)
from app.core.domain.repositories.log import ILogWriteRepository
from app.platform.persistence.postgresql.database import (
    get_postgres_session,
)

# =============================================================================
# Log Repositories - App-scoped (no session concerns)
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


# Re-export the postgres session dep so log handlers can use it if needed
PostgresSessionDep = Annotated[AsyncSession, Depends(get_postgres_session)]
