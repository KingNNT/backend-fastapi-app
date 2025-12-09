"""User read model - optimized for queries."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserReadModel:
    """
    Denormalized read model for user queries.
    Optimized for read operations (CQRS query side).
    """

    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UserReadModel":
        """Create from dictionary."""
        return cls(
            id=str(data.get("id", "")),
            email=str(data.get("email", "")),
            username=str(data.get("username", "")),
            full_name=data.get("full_name"),
            is_active=bool(data.get("is_active", True)),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at", datetime.now()),
            deleted_at=data.get("deleted_at"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
