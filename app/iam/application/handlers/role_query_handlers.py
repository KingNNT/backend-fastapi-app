"""Role query handlers - execute role read operations."""

from typing import Optional, Protocol

from app.iam.application.queries.role.get_role import (
    GetRoleByIdQuery,
    GetRoleByNameQuery,
)
from app.iam.application.queries.role.list_roles import ListRolesQuery
from app.iam.application.read_models.role_read_model import RoleReadModel


class IRoleReadModelRepository(Protocol):
    """Interface for role read model repository."""

    async def get_by_id(self, role_id: str) -> Optional[RoleReadModel]:
        """Get role read model by ID."""
        ...

    async def get_by_name(self, name: str) -> Optional[RoleReadModel]:
        """Get role read model by name."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[RoleReadModel]:
        """List role read models with pagination."""
        ...


class GetRoleByIdHandler:
    """Handler for GetRoleByIdQuery."""

    def __init__(self, repository: IRoleReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetRoleByIdQuery) -> Optional[RoleReadModel]:
        """Execute the get role by ID query."""
        return await self._repository.get_by_id(query.role_id)


class GetRoleByNameHandler:
    """Handler for GetRoleByNameQuery."""

    def __init__(self, repository: IRoleReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetRoleByNameQuery) -> Optional[RoleReadModel]:
        """Execute the get role by name query."""
        return await self._repository.get_by_name(query.name)


class ListRolesHandler:
    """Handler for ListRolesQuery."""

    def __init__(self, repository: IRoleReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListRolesQuery) -> list[RoleReadModel]:
        """Execute the list roles query."""
        return await self._repository.list_all(
            skip=query.skip,
            limit=query.limit,
            include_deleted=query.include_deleted,
        )
