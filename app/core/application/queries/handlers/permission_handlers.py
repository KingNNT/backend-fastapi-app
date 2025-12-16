"""Permission query handlers - execute permission read operations."""

from typing import Optional, Protocol

from app.core.application.queries.permission.get_permission import (
    GetPermissionByIdQuery,
    GetPermissionByNameQuery,
)
from app.core.application.queries.permission.list_permissions import (
    ListPermissionsQuery,
)
from app.core.application.read_models.permission_read_model import PermissionReadModel


class IPermissionReadModelRepository(Protocol):
    """Interface for permission read model repository."""

    async def get_by_id(self, permission_id: str) -> Optional[PermissionReadModel]:
        """Get permission read model by ID."""
        ...

    async def get_by_name(self, name: str) -> Optional[PermissionReadModel]:
        """Get permission read model by name."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[PermissionReadModel]:
        """List permission read models with pagination."""
        ...


class GetPermissionByIdHandler:
    """Handler for GetPermissionByIdQuery."""

    def __init__(self, repository: IPermissionReadModelRepository) -> None:
        self._repository = repository

    async def handle(
        self, query: GetPermissionByIdQuery
    ) -> Optional[PermissionReadModel]:
        """Execute the get permission by ID query."""
        return await self._repository.get_by_id(query.permission_id)


class GetPermissionByNameHandler:
    """Handler for GetPermissionByNameQuery."""

    def __init__(self, repository: IPermissionReadModelRepository) -> None:
        self._repository = repository

    async def handle(
        self, query: GetPermissionByNameQuery
    ) -> Optional[PermissionReadModel]:
        """Execute the get permission by name query."""
        return await self._repository.get_by_name(query.name)


class ListPermissionsHandler:
    """Handler for ListPermissionsQuery."""

    def __init__(self, repository: IPermissionReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListPermissionsQuery) -> list[PermissionReadModel]:
        """Execute the list permissions query."""
        return await self._repository.list_all(
            skip=query.skip,
            limit=query.limit,
            include_deleted=query.include_deleted,
        )
