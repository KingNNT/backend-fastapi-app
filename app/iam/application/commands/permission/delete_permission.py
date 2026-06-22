"""Delete permission command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DeletePermissionCommand:
    """Command to soft delete a permission."""

    permission_id: str
    deleted_by: Optional[str] = None
