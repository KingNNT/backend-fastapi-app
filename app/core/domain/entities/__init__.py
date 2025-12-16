"""Entities - objects with identity."""

from app.core.domain.entities.base import BaseEntity
from app.core.domain.entities.log import Log
from app.core.domain.entities.permission import Permission
from app.core.domain.entities.role import Role
from app.core.domain.entities.user import User

__all__ = [
    "BaseEntity",
    "User",
    "Log",
    "Role",
    "Permission",
]
