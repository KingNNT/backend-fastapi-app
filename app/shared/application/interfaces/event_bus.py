"""Event bus interface - defines event publishing contract."""

from typing import Callable, Protocol, TypeVar

from app.shared.domain.base_event import BaseDomainEvent

T = TypeVar("T", bound=BaseDomainEvent)


class IEventBus(Protocol):
    """
    Interface for event bus implementations.
    Used to publish domain events to interested handlers.
    """

    async def publish(self, event: BaseDomainEvent) -> None:
        """Publish a domain event to all subscribed handlers."""
        ...

    def subscribe(
        self,
        event_type: type[T],
        handler: Callable[[T], None],
    ) -> None:
        """Subscribe a handler to a specific event type."""
        ...

    def unsubscribe(
        self,
        event_type: type[T],
        handler: Callable[[T], None],
    ) -> None:
        """Unsubscribe a handler from a specific event type."""
        ...
