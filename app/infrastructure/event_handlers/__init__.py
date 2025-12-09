"""Event handlers - react to domain events."""

from app.infrastructure.event_handlers.user_event_handlers import UserEventHandler

__all__ = [
    "UserEventHandler",
]
