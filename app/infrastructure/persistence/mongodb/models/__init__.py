"""MongoDB persistence models."""

from app.infrastructure.persistence.mongodb.models.base import BaseDocument
from app.infrastructure.persistence.mongodb.models.log import LogModel

__all__ = [
    "BaseDocument",
    "LogModel",
]
