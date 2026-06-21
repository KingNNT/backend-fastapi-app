"""Permission repository interface - defines data access contract."""

from typing import Optional, Protocol

from app.iam.domain.permission.aggregate import PermissionAggregate
from app.iam.domain.permission.value_objects import PermissionName
from app.shared.domain.ids.permission_id import PermissionId


class IPermissionWriteRepository(Protocol):
    """
    Repository interface for permission write operations (Command side).
    Implementations will be in the infrastructure layer.
    """

    async def save(self, aggregate: PermissionAggregate) -> None:
        """Save a permission aggregate (create or update)."""
        ...

    async def delete(self, aggregate: PermissionAggregate) -> None:
        """Delete a permission aggregate."""
        ...

    async def exists_by_name(self, name: PermissionName) -> bool:
        """Check if a permission with the given name exists."""
        ...


class IPermissionReadRepository(Protocol):
    """
    Repository interface for permission read operations (Query side).
    Implementations will be in the infrastructure layer.
    """

    async def get_by_id(
        self, permission_id: PermissionId
    ) -> Optional[PermissionAggregate]:
        """Get a permission by ID."""
        ...

    async def get_by_name(self, name: PermissionName) -> Optional[PermissionAggregate]:
        """Get a permission by name."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[PermissionAggregate]:
        """List all permissions with pagination."""
        ...

    async def count(self, include_deleted: bool = False) -> int:
        """Count total permissions."""
        ...
