"""Aggregates - consistency boundaries for domain operations."""

from app.core.domain.aggregates.log import LogAggregate
from app.core.domain.aggregates.permission import PermissionAggregate
from app.core.domain.aggregates.role import RoleAggregate
from app.core.domain.aggregates.user import UserAggregate

__all__ = [
    "UserAggregate",
    "LogAggregate",
    "RoleAggregate",
    "PermissionAggregate",
]
