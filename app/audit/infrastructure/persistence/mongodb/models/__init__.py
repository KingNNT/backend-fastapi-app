"""MongoDB persistence models."""

from app.audit.infrastructure.persistence.mongodb.models.base import BaseDocument
from app.audit.infrastructure.persistence.mongodb.models.log import LogModel

__all__ = ["BaseDocument", "LogModel"]
