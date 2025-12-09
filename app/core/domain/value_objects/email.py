"""Email value object - represents a validated email address."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Email value object.
    Immutable and self-validating.
    """

    value: str

    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    @classmethod
    def _is_valid(cls, email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        return bool(cls._EMAIL_PATTERN.match(email))

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Email):
            return self.value.lower() == other.value.lower()
        return False

    def __hash__(self) -> int:
        return hash(self.value.lower())

    @property
    def domain(self) -> str:
        """Extract domain from email."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Extract local part (before @) from email."""
        return self.value.split("@")[0]
