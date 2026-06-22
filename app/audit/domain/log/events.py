"""Log domain events."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from app.shared.domain.base_event import BaseDomainEvent


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class LogCreated(BaseDomainEvent):
    """Event raised when a new log entry is created."""

    log_id: str = ""
    action: str = ""
    user_id: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=utc_now)

    def _payload(self) -> dict[str, Any]:
        return {
            "log_id": self.log_id,
            "action": self.action,
            "user_id": self.user_id,
        }
