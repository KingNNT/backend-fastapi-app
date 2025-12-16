"""Permission read model - optimized for queries."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PermissionReadModel:
    """
    Denormalized read model for permission queries.
    Optimized for read operations (CQRS query side).
    """

    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PermissionReadModel":
        """Create from dictionary."""
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            description=data.get("description"),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at", datetime.now()),
            deleted_at=data.get("deleted_at"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
