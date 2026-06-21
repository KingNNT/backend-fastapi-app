"""Password hasher implementation."""

import hashlib
import secrets


class SimplePasswordHasher:
    """
    Simple password hasher for demonstration.
    In production, use a proper library like passlib with bcrypt.
    """

    def hash(self, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")
        hashed = hashlib.sha256(salt_bytes + password_bytes).hexdigest()
        return f"{salt}${hashed}"

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, stored_hash = hashed.split("$")
            password_bytes = password.encode("utf-8")
            salt_bytes = salt.encode("utf-8")
            computed_hash = hashlib.sha256(salt_bytes + password_bytes).hexdigest()
            return secrets.compare_digest(computed_hash, stored_hash)
        except (ValueError, AttributeError):
            return False
