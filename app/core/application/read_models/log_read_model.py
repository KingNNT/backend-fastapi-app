"""Log read model - optimized for queries."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class LogReadModel:
    """
    Denormalized read model for log queries.
    Optimized for read operations (CQRS query side).
    """

    id: str
    action: str
    user_id: Optional[str]
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "LogReadModel":
        """Create from dictionary."""
        return cls(
            id=str(data.get("id", "")),
            action=str(data.get("action", "")),
            user_id=data.get("user_id"),
            timestamp=data.get("timestamp", datetime.now()),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "action": self.action,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
