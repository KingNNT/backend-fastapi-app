"""Assignment command handlers - manage role and permission assignments."""

from typing import Protocol
from uuid import UUID

from app.core.application.commands.assignment.permission_assignment import (
    AssignPermissionToRoleCommand,
    AssignPermissionToUserCommand,
    RemovePermissionFromRoleCommand,
    RemovePermissionFromUserCommand,
)
from app.core.application.commands.assignment.role_assignment import (
    AssignRoleToUserCommand,
    RemoveRoleFromUserCommand,
)
from app.core.application.interfaces.event_bus import IEventBus
from app.core.domain.events.permission_events import (
    PermissionAssignedToUser,
    PermissionRemovedFromUser,
)
from app.core.domain.events.role_events import (
    PermissionAssignedToRole,
    PermissionRemovedFromRole,
    RoleAssignedToUser,
    RoleRemovedFromUser,
)
from app.core.domain.exceptions.permission import PermissionNotFound
from app.core.domain.exceptions.role import RoleNotFound
from app.core.domain.exceptions.user import UserNotFound


class IAssignmentRepository(Protocol):
    """Interface for assignment operations."""

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


class AssignRoleToUserHandler:
    """Handler for AssignRoleToUserCommand."""

    def __init__(
        self,
        assignment_repository: IAssignmentRepository,
        event_bus: IEventBus,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._event_bus = event_bus

    async def handle(self, command: AssignRoleToUserCommand) -> bool:
        """Execute the assign role to user command."""
        user_id = UUID(command.user_id)
        role_id = UUID(command.role_id)

        # Verify entities exist
        if not await self._assignment_repository.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await self._assignment_repository.role_exists(role_id):
            raise RoleNotFound(command.role_id)

        # Check if already assigned
        if await self._assignment_repository.user_has_role(user_id, role_id):
            return False  # Already assigned

        # Assign role
        await self._assignment_repository.assign_role_to_user(user_id, role_id)

        # Publish event
        await self._event_bus.publish(
            RoleAssignedToUser(
                user_id=command.user_id,
                role_id=command.role_id,
            )
        )

        return True


class RemoveRoleFromUserHandler:
    """Handler for RemoveRoleFromUserCommand."""

    def __init__(
        self,
        assignment_repository: IAssignmentRepository,
        event_bus: IEventBus,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._event_bus = event_bus

    async def handle(self, command: RemoveRoleFromUserCommand) -> bool:
        """Execute the remove role from user command."""
        user_id = UUID(command.user_id)
        role_id = UUID(command.role_id)

        # Verify entities exist
        if not await self._assignment_repository.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await self._assignment_repository.role_exists(role_id):
            raise RoleNotFound(command.role_id)

        # Remove role
        removed = await self._assignment_repository.remove_role_from_user(
            user_id, role_id
        )

        if removed:
            # Publish event
            await self._event_bus.publish(
                RoleRemovedFromUser(
                    user_id=command.user_id,
                    role_id=command.role_id,
                )
            )

        return removed


class AssignPermissionToUserHandler:
    """Handler for AssignPermissionToUserCommand."""

    def __init__(
        self,
        assignment_repository: IAssignmentRepository,
        event_bus: IEventBus,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._event_bus = event_bus

    async def handle(self, command: AssignPermissionToUserCommand) -> bool:
        """Execute the assign permission to user command."""
        user_id = UUID(command.user_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await self._assignment_repository.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await self._assignment_repository.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Check if already assigned
        if await self._assignment_repository.user_has_direct_permission(
            user_id, permission_id
        ):
            return False  # Already assigned

        # Assign permission
        await self._assignment_repository.assign_permission_to_user(
            user_id, permission_id
        )

        # Publish event
        await self._event_bus.publish(
            PermissionAssignedToUser(
                user_id=command.user_id,
                permission_id=command.permission_id,
            )
        )

        return True


class RemovePermissionFromUserHandler:
    """Handler for RemovePermissionFromUserCommand."""

    def __init__(
        self,
        assignment_repository: IAssignmentRepository,
        event_bus: IEventBus,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._event_bus = event_bus

    async def handle(self, command: RemovePermissionFromUserCommand) -> bool:
        """Execute the remove permission from user command."""
        user_id = UUID(command.user_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await self._assignment_repository.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await self._assignment_repository.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Remove permission
        removed = await self._assignment_repository.remove_permission_from_user(
            user_id, permission_id
        )

        if removed:
            # Publish event
            await self._event_bus.publish(
                PermissionRemovedFromUser(
                    user_id=command.user_id,
                    permission_id=command.permission_id,
                )
            )

        return removed


class AssignPermissionToRoleHandler:
    """Handler for AssignPermissionToRoleCommand."""

    def __init__(
        self,
        assignment_repository: IAssignmentRepository,
        event_bus: IEventBus,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._event_bus = event_bus

    async def handle(self, command: AssignPermissionToRoleCommand) -> bool:
        """Execute the assign permission to role command."""
        role_id = UUID(command.role_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await self._assignment_repository.role_exists(role_id):
            raise RoleNotFound(command.role_id)
        if not await self._assignment_repository.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Check if already assigned
        if await self._assignment_repository.role_has_permission(
            role_id, permission_id
        ):
            return False  # Already assigned

        # Assign permission
        await self._assignment_repository.assign_permission_to_role(
            role_id, permission_id
        )

        # Publish event
        await self._event_bus.publish(
            PermissionAssignedToRole(
                role_id=command.role_id,
                permission_id=command.permission_id,
            )
        )

        return True


class RemovePermissionFromRoleHandler:
    """Handler for RemovePermissionFromRoleCommand."""

    def __init__(
        self,
        assignment_repository: IAssignmentRepository,
        event_bus: IEventBus,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._event_bus = event_bus

    async def handle(self, command: RemovePermissionFromRoleCommand) -> bool:
        """Execute the remove permission from role command."""
        role_id = UUID(command.role_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await self._assignment_repository.role_exists(role_id):
            raise RoleNotFound(command.role_id)
        if not await self._assignment_repository.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Remove permission
        removed = await self._assignment_repository.remove_permission_from_role(
            role_id, permission_id
        )

        if removed:
            # Publish event
            await self._event_bus.publish(
                PermissionRemovedFromRole(
                    role_id=command.role_id,
                    permission_id=command.permission_id,
                )
            )

        return removed
