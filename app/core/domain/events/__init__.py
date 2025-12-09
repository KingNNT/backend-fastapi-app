"""Domain events - records of things that happened in the domain."""

from app.core.domain.events.base import BaseDomainEvent
from app.core.domain.events.log_events import LogCreated
from app.core.domain.events.user_events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserEmailUpdated,
    UserPasswordUpdated,
    UserUpdated,
)

__all__ = [
    "BaseDomainEvent",
    "UserCreated",
    "UserUpdated",
    "UserDeleted",
    "UserDeactivated",
    "UserActivated",
    "UserEmailUpdated",
    "UserPasswordUpdated",
    "LogCreated",
]
