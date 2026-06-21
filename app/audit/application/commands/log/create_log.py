"""Create log command."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class CreateLogCommand:
    """Command to create a new log entry."""

    action: str
    user_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
