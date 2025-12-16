"""Update permission command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UpdatePermissionCommand:
    """Command to update an existing permission."""

    permission_id: str
    name: Optional[str] = None
    description: Optional[str] = None
