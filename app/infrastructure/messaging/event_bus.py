"""In-memory event bus implementation."""

import logging
from collections import defaultdict
from typing import Callable, TypeVar

from app.core.domain.events.base import BaseDomainEvent

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseDomainEvent)


class InMemoryEventBus:
    """In-memory event bus for publishing domain events."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(
        self,
        event_type: type[T],
        handler: Callable[[T], None],
    ) -> None:
        """Subscribe a handler to a specific event type."""
        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type.__name__}")

    def unsubscribe(
        self,
        event_type: type[T],
        handler: Callable[[T], None],
    ) -> None:
        """Unsubscribe a handler from a specific event type."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(f"Unsubscribed handler from {event_type.__name__}")

    async def publish(self, event: BaseDomainEvent) -> None:
        """Publish a domain event to all subscribed handlers."""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        logger.info(
            f"Publishing event {event_type.__name__} to {len(handlers)} handlers"
        )

        for handler in handlers:
            try:
                result = handler(event)
                # Support both sync and async handlers
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                logger.error(
                    f"Error in event handler for {event_type.__name__}: {e}",
                    exc_info=True,
                )
                # Continue processing other handlers even if one fails
