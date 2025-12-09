"""Base domain event class."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class BaseDomainEvent:
    """
    Base class for all domain events.
    Domain events are immutable records of something that happened.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.__class__.__name__,
            "occurred_at": self.occurred_at.isoformat(),
            **self._payload(),
        }

    def _payload(self) -> dict[str, Any]:
        """Override in subclasses to provide event-specific payload."""
        return {}
