"""Role repository interface - defines data access contract."""

from typing import Optional, Protocol

from app.core.domain.aggregates.role import RoleAggregate
from app.core.domain.value_objects.role_name import RoleName
from app.shared.domain.ids.role_id import RoleId


class IRoleWriteRepository(Protocol):
    """
    Repository interface for role write operations (Command side).
    Implementations will be in the infrastructure layer.
    """

    async def save(self, aggregate: RoleAggregate) -> None:
        """Save a role aggregate (create or update)."""
        ...

    async def delete(self, aggregate: RoleAggregate) -> None:
        """Delete a role aggregate."""
        ...

    async def exists_by_name(self, name: RoleName) -> bool:
        """Check if a role with the given name exists."""
        ...


class IRoleReadRepository(Protocol):
    """
    Repository interface for role read operations (Query side).
    Implementations will be in the infrastructure layer.
    """

    async def get_by_id(self, role_id: RoleId) -> Optional[RoleAggregate]:
        """Get a role by ID."""
        ...

    async def get_by_name(self, name: RoleName) -> Optional[RoleAggregate]:
        """Get a role by name."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[RoleAggregate]:
        """List all roles with pagination."""
        ...

    async def count(self, include_deleted: bool = False) -> int:
        """Count total roles."""
        ...
