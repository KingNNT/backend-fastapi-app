"""Assignment repository interface — defines contract for relationship operations."""

from typing import Protocol
from uuid import UUID


class IAssignmentRepository(Protocol):
    """Repository interface for assignment operations (roles and permissions).

    This interface defines operations for managing the relationships between
    users, roles, and permissions. Implementations handle junction table operations.
    """

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> None:
        """Assign a role to a user."""
        ...

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Remove a role from a user."""
        ...

    async def user_has_role(self, user_id: UUID, role_id: UUID) -> bool:
        """Check if user has a role."""
        ...

    async def assign_permission_to_user(
        self, user_id: UUID, permission_id: UUID
    ) -> None:
        """Assign a permission to a user."""
        ...

    async def remove_permission_from_user(
        self, user_id: UUID, permission_id: UUID
    ) -> bool:
        """Remove a permission from a user."""
        ...

    async def user_has_direct_permission(
        self, user_id: UUID, permission_id: UUID
    ) -> bool:
        """Check if user has a direct permission."""
        ...

    async def assign_permission_to_role(
        self, role_id: UUID, permission_id: UUID
    ) -> None:
        """Assign a permission to a role."""
        ...

    async def remove_permission_from_role(
        self, role_id: UUID, permission_id: UUID
    ) -> bool:
        """Remove a permission from a role."""
        ...

    async def role_has_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        """Check if role has a permission."""
        ...

    async def user_exists(self, user_id: UUID) -> bool:
        """Check if user exists."""
        ...

    async def role_exists(self, role_id: UUID) -> bool:
        """Check if role exists."""
        ...

    async def permission_exists(self, permission_id: UUID) -> bool:
        """Check if permission exists."""
        ...
