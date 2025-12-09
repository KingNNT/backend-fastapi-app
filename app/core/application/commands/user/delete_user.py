"""Delete user command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DeleteUserCommand:
    """Command to soft delete a user."""

    user_id: str
    deleted_by: Optional[str] = None
