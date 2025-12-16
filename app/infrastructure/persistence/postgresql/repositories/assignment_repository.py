"""Assignment repository for managing junction table operations."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.postgresql.models.permission import PermissionModel
from app.infrastructure.persistence.postgresql.models.role import RoleModel
from app.infrastructure.persistence.postgresql.models.role_has_permissions import (
    RoleHasPermissionsModel,
)
from app.infrastructure.persistence.postgresql.models.user import UserModel
from app.infrastructure.persistence.postgresql.models.user_has_permission import (
    UserHasPermissionModel,
)
from app.infrastructure.persistence.postgresql.models.user_has_role import (
    UserHasRoleModel,
)


def _utc_now() -> datetime:
    """Get current UTC time (timezone-naive for database compatibility)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AssignmentRepository:
    """Repository for managing role and permission assignments."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ============ User-Role Assignments ============

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> None:
        """Assign a role to a user."""
        assignment = UserHasRoleModel(
            id=uuid4(),
            user_id=user_id,
            role_id=role_id,
            created_at=_utc_now(),
        )
        self._session.add(assignment)
        await self._session.commit()

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Remove a role from a user. Returns True if removed, False if not found."""
        stmt = delete(UserHasRoleModel).where(
            UserHasRoleModel.user_id == user_id,
            UserHasRoleModel.role_id == role_id,
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def user_has_role(self, user_id: UUID, role_id: UUID) -> bool:
        """Check if a user has a specific role."""
        stmt = select(UserHasRoleModel).where(
            UserHasRoleModel.user_id == user_id,
            UserHasRoleModel.role_id == role_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_role_ids(self, user_id: UUID) -> list[UUID]:
        """Get all role IDs assigned to a user."""
        stmt = select(UserHasRoleModel.role_id).where(
            UserHasRoleModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_users_with_role(self, role_id: UUID) -> list[UUID]:
        """Get all user IDs that have a specific role."""
        stmt = select(UserHasRoleModel.user_id).where(
            UserHasRoleModel.role_id == role_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ============ User-Permission Assignments (Direct) ============

    async def assign_permission_to_user(
        self, user_id: UUID, permission_id: UUID
    ) -> None:
        """Assign a permission directly to a user."""
        assignment = UserHasPermissionModel(
            id=uuid4(),
            user_id=user_id,
            permission_id=permission_id,
            created_at=_utc_now(),
        )
        self._session.add(assignment)
        await self._session.commit()

    async def remove_permission_from_user(
        self, user_id: UUID, permission_id: UUID
    ) -> bool:
        """Remove a direct permission from a user. Returns True if removed."""
        stmt = delete(UserHasPermissionModel).where(
            UserHasPermissionModel.user_id == user_id,
            UserHasPermissionModel.permission_id == permission_id,
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def user_has_direct_permission(
        self, user_id: UUID, permission_id: UUID
    ) -> bool:
        """Check if a user has a specific permission directly assigned."""
        stmt = select(UserHasPermissionModel).where(
            UserHasPermissionModel.user_id == user_id,
            UserHasPermissionModel.permission_id == permission_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_direct_permission_ids(self, user_id: UUID) -> list[UUID]:
        """Get all permission IDs directly assigned to a user."""
        stmt = select(UserHasPermissionModel.permission_id).where(
            UserHasPermissionModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ============ Role-Permission Assignments ============

    async def assign_permission_to_role(
        self, role_id: UUID, permission_id: UUID
    ) -> None:
        """Assign a permission to a role."""
        assignment = RoleHasPermissionsModel(
            id=uuid4(),
            role_id=role_id,
            permission_id=permission_id,
            created_at=_utc_now(),
        )
        self._session.add(assignment)
        await self._session.commit()

    async def remove_permission_from_role(
        self, role_id: UUID, permission_id: UUID
    ) -> bool:
        """Remove a permission from a role. Returns True if removed."""
        stmt = delete(RoleHasPermissionsModel).where(
            RoleHasPermissionsModel.role_id == role_id,
            RoleHasPermissionsModel.permission_id == permission_id,
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def role_has_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        """Check if a role has a specific permission."""
        stmt = select(RoleHasPermissionsModel).where(
            RoleHasPermissionsModel.role_id == role_id,
            RoleHasPermissionsModel.permission_id == permission_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_role_permission_ids(self, role_id: UUID) -> list[UUID]:
        """Get all permission IDs assigned to a role."""
        stmt = select(RoleHasPermissionsModel.permission_id).where(
            RoleHasPermissionsModel.role_id == role_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_roles_with_permission(self, permission_id: UUID) -> list[UUID]:
        """Get all role IDs that have a specific permission."""
        stmt = select(RoleHasPermissionsModel.role_id).where(
            RoleHasPermissionsModel.permission_id == permission_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ============ Effective Permissions (User's full permission set) ============

    async def get_user_effective_permission_ids(self, user_id: UUID) -> list[UUID]:
        """
        Get all effective permission IDs for a user.

        This includes:
        - Direct permissions assigned to the user
        - Permissions from all roles assigned to the user
        """
        # Get direct permissions
        direct_permissions = set(await self.get_user_direct_permission_ids(user_id))

        # Get role-based permissions
        role_ids = await self.get_user_role_ids(user_id)
        role_permissions: set[UUID] = set()
        for role_id in role_ids:
            perms = await self.get_role_permission_ids(role_id)
            role_permissions.update(perms)

        # Combine and return unique permissions
        all_permissions = direct_permissions | role_permissions
        return list(all_permissions)

    # ============ Entity Existence Checks ============

    async def user_exists(self, user_id: UUID) -> bool:
        """Check if a user exists."""
        stmt = select(UserModel.id).where(
            UserModel.id == user_id,
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def role_exists(self, role_id: UUID) -> bool:
        """Check if a role exists."""
        stmt = select(RoleModel.id).where(
            RoleModel.id == role_id,
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def permission_exists(self, permission_id: UUID) -> bool:
        """Check if a permission exists."""
        stmt = select(PermissionModel.id).where(
            PermissionModel.id == permission_id,
            PermissionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
