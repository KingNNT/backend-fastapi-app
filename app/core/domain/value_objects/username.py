"""Username value object - represents a validated username."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Username:
    """
    Username value object.
    Immutable and self-validating.

    Rules:
    - 3-50 characters
    - Alphanumeric, underscores, and hyphens only
    - Must start with a letter
    """

    value: str

    _MIN_LENGTH = 3
    _MAX_LENGTH = 50
    _USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid username: {self.value}")

    @classmethod
    def _is_valid(cls, username: str) -> bool:
        """Validate username format."""
        if not username or not isinstance(username, str):
            return False
        if len(username) < cls._MIN_LENGTH or len(username) > cls._MAX_LENGTH:
            return False
        return bool(cls._USERNAME_PATTERN.match(username))

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Username):
            return self.value.lower() == other.value.lower()
        return False

    def __hash__(self) -> int:
        return hash(self.value.lower())
