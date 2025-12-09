"""Read models - optimized for queries (CQRS query side)."""

from app.core.application.read_models.log_read_model import LogReadModel
from app.core.application.read_models.user_read_model import UserReadModel

__all__ = [
    "UserReadModel",
    "LogReadModel",
]
