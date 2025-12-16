"""PostgreSQL mappers."""

from app.infrastructure.persistence.postgresql.mappers.permission import (
    PermissionMapper,
)
from app.infrastructure.persistence.postgresql.mappers.role import RoleMapper
from app.infrastructure.persistence.postgresql.mappers.user import UserMapper

__all__ = [
    "PermissionMapper",
    "RoleMapper",
    "UserMapper",
]
