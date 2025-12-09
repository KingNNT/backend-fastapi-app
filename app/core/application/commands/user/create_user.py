"""Create user command."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateUserCommand:
    """Command to create a new user."""

    email: str
    username: str
    password: str
    full_name: Optional[str] = None
