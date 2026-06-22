"""Create permission command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreatePermissionCommand:
    """Command to create a new permission."""

    name: str
    description: Optional[str] = None
