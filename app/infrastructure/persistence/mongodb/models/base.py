"""Base model for MongoDB persistence."""

from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


class BaseDocument(Document):
    """Base document with common fields for MongoDB entities."""

    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        """Beanie document settings."""

        use_state_management = True
