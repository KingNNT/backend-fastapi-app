"""Dependency injection for repositories."""

from app.core.application.queries.handlers.log_handlers import ILogReadModelRepository
from app.core.application.queries.handlers.user_handlers import IUserReadModelRepository
from app.core.domain.repositories.log import ILogWriteRepository
from app.core.domain.repositories.user import IUserRepository

# These will be implemented in the infrastructure layer
# For now, we provide placeholder functions that will be overwritten
# when the infrastructure layer is initialized

_user_repository: IUserRepository | None = None
_log_repository: ILogWriteRepository | None = None
_user_read_model_repository: IUserReadModelRepository | None = None
_log_read_model_repository: ILogReadModelRepository | None = None


def set_user_repository(repo: IUserRepository) -> None:
    """Set the user repository implementation."""
    global _user_repository
    _user_repository = repo


def set_log_repository(repo: ILogWriteRepository) -> None:
    """Set the log repository implementation."""
    global _log_repository
    _log_repository = repo


def set_user_read_model_repository(repo: IUserReadModelRepository) -> None:
    """Set the user read model repository implementation."""
    global _user_read_model_repository
    _user_read_model_repository = repo


def set_log_read_model_repository(repo: ILogReadModelRepository) -> None:
    """Set the log read model repository implementation."""
    global _log_read_model_repository
    _log_read_model_repository = repo


def get_user_repository() -> IUserRepository:
    """Get the user repository instance."""
    if _user_repository is None:
        raise RuntimeError("User repository not initialized")
    return _user_repository


def get_log_repository() -> ILogWriteRepository:
    """Get the log repository instance."""
    if _log_repository is None:
        raise RuntimeError("Log repository not initialized")
    return _log_repository


def get_user_read_model_repository() -> IUserReadModelRepository:
    """Get the user read model repository instance."""
    if _user_read_model_repository is None:
        raise RuntimeError("User read model repository not initialized")
    return _user_read_model_repository


def get_log_read_model_repository() -> ILogReadModelRepository:
    """Get the log read model repository instance."""
    if _log_read_model_repository is None:
        raise RuntimeError("Log read model repository not initialized")
    return _log_read_model_repository
