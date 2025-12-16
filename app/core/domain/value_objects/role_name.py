"""RoleName value object - represents a validated role name."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RoleName:
    """
    Role name value object.
    Immutable and self-validating.

    Rules:
    - 2-100 characters
    - Alphanumeric, underscores, hyphens, and spaces allowed
    - Must start with a letter
    """

    value: str

    _MIN_LENGTH = 2
    _MAX_LENGTH = 100
    _NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\- ]*$")

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid role name: {self.value}")

    @classmethod
    def _is_valid(cls, name: str) -> bool:
        """Validate role name format."""
        if not name or not isinstance(name, str):
            return False
        if len(name) < cls._MIN_LENGTH or len(name) > cls._MAX_LENGTH:
            return False
        return bool(cls._NAME_PATTERN.match(name))

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoleName):
            return self.value.lower() == other.value.lower()
        return False

    def __hash__(self) -> int:
        return hash(self.value.lower())
