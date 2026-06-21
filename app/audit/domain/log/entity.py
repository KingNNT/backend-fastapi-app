"""Log entity - represents an audit log entry in the domain."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from app.audit.domain.log.value_objects import Action
from app.shared.domain.ids.log_id import LogId


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


@dataclass
class Log:
    """
    Log entity for audit trail.
    Stored in MongoDB.

    Note: Log entries are immutable after creation (no soft delete, no updates).
    """

    id: Optional[LogId] = None  # Assigned by MongoDB
    action: Action = field(default_factory=lambda: Action.custom("unknown"))
    user_id: Optional[str] = None  # Reference to user who performed action
    timestamp: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Ensure action is properly typed
        if isinstance(self.action, str):
            object.__setattr__(self, "action", Action.custom(self.action))

    @classmethod
    def create(
        cls,
        action: Action,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Log":
        """Factory method to create a new log entry."""
        return cls(
            action=action,
            user_id=user_id,
            timestamp=utc_now(),
            metadata=metadata or {},
        )

    @classmethod
    def user_created_log(cls, user_id: str, email: str) -> "Log":
        """Create a log entry for user creation."""
        return cls.create(
            action=Action.user_created(),
            user_id=user_id,
            metadata={"email": email, "event": "user_created"},
        )

    @classmethod
    def user_updated_log(cls, user_id: str, changes: dict[str, Any]) -> "Log":
        """Create a log entry for user update."""
        return cls.create(
            action=Action.user_updated(),
            user_id=user_id,
            metadata={"changes": changes, "event": "user_updated"},
        )

    @classmethod
    def user_deleted_log(cls, user_id: str) -> "Log":
        """Create a log entry for user deletion."""
        return cls.create(
            action=Action.user_deleted(),
            user_id=user_id,
            metadata={"event": "user_deleted"},
        )

    @property
    def action_str(self) -> str:
        """Get action as string."""
        return str(self.action)

    @property
    def id_str(self) -> Optional[str]:
        """Get id as string."""
        return str(self.id) if self.id else None
