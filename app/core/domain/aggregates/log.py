"""Log aggregate - consistency boundary for log operations."""

from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.domain.entities.log import Log
from app.core.domain.events.log_events import LogCreated
from app.core.domain.value_objects.action import Action
from app.shared.domain.base_event import BaseDomainEvent
from app.shared.domain.ids.log_id import LogId


@dataclass
class LogAggregate:
    """
    Log aggregate root - ensures consistency for log operations.
    Note: Logs are immutable after creation (append-only audit trail).
    """

    _log: Log
    _events: list[BaseDomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        action: Action,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "LogAggregate":
        """Factory method to create a new log aggregate."""
        log = Log.create(
            action=action,
            user_id=user_id,
            metadata=metadata,
        )
        aggregate = cls(_log=log)
        aggregate._events.append(
            LogCreated(
                log_id=log.id_str or "",
                action=log.action_str,
                user_id=user_id,
            )
        )
        return aggregate

    @classmethod
    def create_user_created_log(cls, user_id: str, email: str) -> "LogAggregate":
        """Create a log for user creation."""
        log = Log.user_created_log(user_id=user_id, email=email)
        aggregate = cls(_log=log)
        aggregate._events.append(
            LogCreated(
                log_id=log.id_str or "",
                action=log.action_str,
                user_id=user_id,
            )
        )
        return aggregate

    @classmethod
    def create_user_updated_log(
        cls, user_id: str, changes: dict[str, Any]
    ) -> "LogAggregate":
        """Create a log for user update."""
        log = Log.user_updated_log(user_id=user_id, changes=changes)
        aggregate = cls(_log=log)
        aggregate._events.append(
            LogCreated(
                log_id=log.id_str or "",
                action=log.action_str,
                user_id=user_id,
            )
        )
        return aggregate

    @classmethod
    def create_user_deleted_log(cls, user_id: str) -> "LogAggregate":
        """Create a log for user deletion."""
        log = Log.user_deleted_log(user_id=user_id)
        aggregate = cls(_log=log)
        aggregate._events.append(
            LogCreated(
                log_id=log.id_str or "",
                action=log.action_str,
                user_id=user_id,
            )
        )
        return aggregate

    @classmethod
    def reconstitute(cls, log: Log) -> "LogAggregate":
        """Reconstitute aggregate from existing log entity (from repository)."""
        return cls(_log=log)

    @property
    def log(self) -> Log:
        """Get the underlying log entity."""
        return self._log

    @property
    def id(self) -> Optional[LogId]:
        """Get log ID."""
        return self._log.id

    @property
    def id_str(self) -> Optional[str]:
        """Get log ID as string."""
        return self._log.id_str

    @property
    def events(self) -> list[BaseDomainEvent]:
        """Get domain events raised by this aggregate."""
        return self._events.copy()

    def clear_events(self) -> None:
        """Clear domain events after they've been dispatched."""
        self._events.clear()

    def set_id(self, log_id: LogId) -> None:
        """Set the log ID (called by repository after persistence)."""
        object.__setattr__(self._log, "id", log_id)
