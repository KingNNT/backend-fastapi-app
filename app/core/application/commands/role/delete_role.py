"""Delete role command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DeleteRoleCommand:
    """Command to soft delete a role."""

    role_id: str
    deleted_by: Optional[str] = None
