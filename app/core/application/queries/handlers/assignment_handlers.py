"""Assignment query handlers - read assignment data."""

from typing import Protocol
from uuid import UUID

from app.core.application.queries.assignment.get_assignments import (
    GetRolePermissionsQuery,
    GetUserEffectivePermissionsQuery,
    GetUserRolesQuery,
)
from app.core.application.read_models.permission_read_model import PermissionReadModel
from app.core.application.read_models.role_read_model import RoleReadModel


class IAssignmentQueryRepository(Protocol):
    """Interface for querying assignment data."""

    async def get_user_role_ids(self, user_id: UUID) -> list[UUID]:
        """Get all role IDs assigned to a user."""
        ...

    async def get_user_effective_permission_ids(self, user_id: UUID) -> list[UUID]:
        """Get all effective permission IDs for a user."""
        ...

    async def get_role_permission_ids(self, role_id: UUID) -> list[UUID]:
        """Get all permission IDs assigned to a role."""
        ...


class IRoleReadModelRepository(Protocol):
    """Interface for reading roles."""

    async def get_by_ids(self, role_ids: list[str]) -> list[RoleReadModel]:
        """Get roles by IDs."""
        ...


class IPermissionReadModelRepository(Protocol):
    """Interface for reading permissions."""

    async def get_by_ids(self, permission_ids: list[str]) -> list[PermissionReadModel]:
        """Get permissions by IDs."""
        ...


class GetUserRolesHandler:
    """Handler for GetUserRolesQuery."""

    def __init__(
        self,
        assignment_repository: IAssignmentQueryRepository,
        role_repository: IRoleReadModelRepository,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._role_repository = role_repository

    async def handle(self, query: GetUserRolesQuery) -> list[RoleReadModel]:
        """Execute the get user roles query."""
        user_id = UUID(query.user_id)

        # Get role IDs
        role_ids = await self._assignment_repository.get_user_role_ids(user_id)

        if not role_ids:
            return []

        # Get role read models
        role_id_strs = [str(rid) for rid in role_ids]
        return await self._role_repository.get_by_ids(role_id_strs)


class GetUserEffectivePermissionsHandler:
    """Handler for GetUserEffectivePermissionsQuery."""

    def __init__(
        self,
        assignment_repository: IAssignmentQueryRepository,
        permission_repository: IPermissionReadModelRepository,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._permission_repository = permission_repository

    async def handle(
        self, query: GetUserEffectivePermissionsQuery
    ) -> list[PermissionReadModel]:
        """Execute the get user effective permissions query."""
        user_id = UUID(query.user_id)

        # Get effective permission IDs (direct + role-based)
        permission_ids = (
            await self._assignment_repository.get_user_effective_permission_ids(user_id)
        )

        if not permission_ids:
            return []

        # Get permission read models
        permission_id_strs = [str(pid) for pid in permission_ids]
        return await self._permission_repository.get_by_ids(permission_id_strs)


class GetRolePermissionsHandler:
    """Handler for GetRolePermissionsQuery."""

    def __init__(
        self,
        assignment_repository: IAssignmentQueryRepository,
        permission_repository: IPermissionReadModelRepository,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._permission_repository = permission_repository

    async def handle(self, query: GetRolePermissionsQuery) -> list[PermissionReadModel]:
        """Execute the get role permissions query."""
        role_id = UUID(query.role_id)

        # Get permission IDs
        permission_ids = await self._assignment_repository.get_role_permission_ids(
            role_id
        )

        if not permission_ids:
            return []

        # Get permission read models
        permission_id_strs = [str(pid) for pid in permission_ids]
        return await self._permission_repository.get_by_ids(permission_id_strs)
