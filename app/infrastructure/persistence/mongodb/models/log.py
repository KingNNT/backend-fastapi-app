"""Log model for MongoDB persistence."""

from datetime import datetime, timezone
from typing import Any, Optional

from beanie import Document, Indexed
from pydantic import Field


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


class LogModel(Document):
    """Log persistence model for MongoDB (Write side)."""

    action: Indexed(str) = Field(..., description="Action type")  # type: ignore
    user_id: Optional[Indexed(str)] = Field(  # type: ignore
        default=None, description="User ID associated with the log"
    )
    timestamp: Indexed(datetime) = Field(  # type: ignore
        default_factory=utc_now, description="Log timestamp"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Log metadata")

    class Settings:
        """Beanie document settings."""

        name = "logs"
        use_state_management = True
