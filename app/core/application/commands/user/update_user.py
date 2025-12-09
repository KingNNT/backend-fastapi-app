"""Update user command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UpdateUserCommand:
    """Command to update an existing user."""

    user_id: str
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
