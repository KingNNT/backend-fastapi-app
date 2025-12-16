"""Dependency injection for repositories."""

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

# These will be implemented in the infrastructure layer
# For now, we provide placeholder functions that will be overwritten
# when the infrastructure layer is initialized

_user_repository: IUserRepository | None = None
_log_repository: ILogWriteRepository | None = None
_user_read_model_repository: IUserReadModelRepository | None = None
_log_read_model_repository: ILogReadModelRepository | None = None
_role_repository: IRoleRepository | None = None
_permission_repository: IPermissionRepository | None = None
_role_read_model_repository: IRoleReadModelRepository | None = None
_permission_read_model_repository: IPermissionReadModelRepository | None = None
_assignment_repository: IAssignmentQueryRepository | None = None


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


# Role repository
def set_role_repository(repo: IRoleRepository) -> None:
    """Set the role repository implementation."""
    global _role_repository
    _role_repository = repo


def get_role_repository() -> IRoleRepository:
    """Get the role repository instance."""
    if _role_repository is None:
        raise RuntimeError("Role repository not initialized")
    return _role_repository


def set_role_read_model_repository(repo: IRoleReadModelRepository) -> None:
    """Set the role read model repository implementation."""
    global _role_read_model_repository
    _role_read_model_repository = repo


def get_role_read_model_repository() -> IRoleReadModelRepository:
    """Get the role read model repository instance."""
    if _role_read_model_repository is None:
        raise RuntimeError("Role read model repository not initialized")
    return _role_read_model_repository


# Permission repository
def set_permission_repository(repo: IPermissionRepository) -> None:
    """Set the permission repository implementation."""
    global _permission_repository
    _permission_repository = repo


def get_permission_repository() -> IPermissionRepository:
    """Get the permission repository instance."""
    if _permission_repository is None:
        raise RuntimeError("Permission repository not initialized")
    return _permission_repository


def set_permission_read_model_repository(repo: IPermissionReadModelRepository) -> None:
    """Set the permission read model repository implementation."""
    global _permission_read_model_repository
    _permission_read_model_repository = repo


def get_permission_read_model_repository() -> IPermissionReadModelRepository:
    """Get the permission read model repository instance."""
    if _permission_read_model_repository is None:
        raise RuntimeError("Permission read model repository not initialized")
    return _permission_read_model_repository


# Assignment repository
def set_assignment_repository(repo: IAssignmentQueryRepository) -> None:
    """Set the assignment repository implementation."""
    global _assignment_repository
    _assignment_repository = repo


def get_assignment_repository() -> IAssignmentQueryRepository:
    """Get the assignment repository instance."""
    if _assignment_repository is None:
        raise RuntimeError("Assignment repository not initialized")
    return _assignment_repository
