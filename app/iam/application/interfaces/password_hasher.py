"""Password hasher interface — IAM-specific infrastructure contract."""

from typing import Protocol


class IPasswordHasher(Protocol):
    """Interface for password hashing."""

    def hash(self, password: str) -> str:
        """Hash a password."""
        ...

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        ...
