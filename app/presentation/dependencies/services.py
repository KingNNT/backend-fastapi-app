"""Dependency injection for services."""

from fastapi import Depends

from app.core.application.commands.handlers.user_handlers import IPasswordHasher
from app.core.application.interfaces.event_bus import IEventBus
from app.core.domain.services.user_domain_service import UserDomainService
from app.presentation.dependencies.repositories import get_user_repository

# These will be implemented in the infrastructure layer
_event_bus: IEventBus | None = None
_password_hasher: IPasswordHasher | None = None


def set_event_bus(bus: IEventBus) -> None:
    """Set the event bus implementation."""
    global _event_bus
    _event_bus = bus


def set_password_hasher(hasher: IPasswordHasher) -> None:
    """Set the password hasher implementation."""
    global _password_hasher
    _password_hasher = hasher


def get_event_bus() -> IEventBus:
    """Get the event bus instance."""
    if _event_bus is None:
        raise RuntimeError("Event bus not initialized")
    return _event_bus


def get_password_hasher() -> IPasswordHasher:
    """Get the password hasher instance."""
    if _password_hasher is None:
        raise RuntimeError("Password hasher not initialized")
    return _password_hasher


def get_user_domain_service(
    repository=Depends(get_user_repository),
) -> UserDomainService:
    """Get the user domain service instance."""
    return UserDomainService(user_read_repository=repository)
