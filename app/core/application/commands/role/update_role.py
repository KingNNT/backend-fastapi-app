"""Update role command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UpdateRoleCommand:
    """Command to update an existing role."""

    role_id: str
    name: Optional[str] = None
    description: Optional[str] = None
