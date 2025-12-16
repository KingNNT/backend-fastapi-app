"""Create role command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateRoleCommand:
    """Command to create a new role."""

    name: str
    description: Optional[str] = None
