"""Assignment command handlers - manage role and permission assignments.

All handlers use the Unit of Work pattern: they receive IIamUnitOfWork via
the handle() method and access the assignment repository via uow.assignments.
Events are added via uow.add_event() and published after commit.
"""

from uuid import UUID

from app.iam.application.commands.assignment.permission_assignment import (
    AssignPermissionToRoleCommand,
    AssignPermissionToUserCommand,
    RemovePermissionFromRoleCommand,
    RemovePermissionFromUserCommand,
)
from app.iam.application.commands.assignment.role_assignment import (
    AssignRoleToUserCommand,
    RemoveRoleFromUserCommand,
)
from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork
from app.iam.domain.permission.events import (
    PermissionAssignedToUser,
    PermissionRemovedFromUser,
)
from app.iam.domain.permission.exceptions import PermissionNotFound
from app.iam.domain.role.events import (
    PermissionAssignedToRole,
    PermissionRemovedFromRole,
    RoleAssignedToUser,
    RoleRemovedFromUser,
)
from app.iam.domain.role.exceptions import RoleNotFound
from app.iam.domain.user.exceptions import UserNotFound


class AssignRoleToUserHandler:
    """Handler for AssignRoleToUserCommand."""

    async def handle(
        self, command: AssignRoleToUserCommand, uow: IIamUnitOfWork
    ) -> bool:
        """Execute the assign role to user command."""
        user_id = UUID(command.user_id)
        role_id = UUID(command.role_id)

        # Verify entities exist
        if not await uow.assignments.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await uow.assignments.role_exists(role_id):
            raise RoleNotFound(command.role_id)

        # Check if already assigned
        if await uow.assignments.user_has_role(user_id, role_id):
            return False  # Already assigned

        # Assign role
        await uow.assignments.assign_role_to_user(user_id, role_id)

        # Queue event for publishing after commit
        uow.add_event(
            RoleAssignedToUser(
                user_id=command.user_id,
                role_id=command.role_id,
            )
        )

        return True


class RemoveRoleFromUserHandler:
    """Handler for RemoveRoleFromUserCommand."""

    async def handle(
        self, command: RemoveRoleFromUserCommand, uow: IIamUnitOfWork
    ) -> bool:
        """Execute the remove role from user command."""
        user_id = UUID(command.user_id)
        role_id = UUID(command.role_id)

        # Verify entities exist
        if not await uow.assignments.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await uow.assignments.role_exists(role_id):
            raise RoleNotFound(command.role_id)

        # Remove role
        removed = await uow.assignments.remove_role_from_user(user_id, role_id)

        if removed:
            uow.add_event(
                RoleRemovedFromUser(
                    user_id=command.user_id,
                    role_id=command.role_id,
                )
            )

        return removed


class AssignPermissionToUserHandler:
    """Handler for AssignPermissionToUserCommand."""

    async def handle(
        self, command: AssignPermissionToUserCommand, uow: IIamUnitOfWork
    ) -> bool:
        """Execute the assign permission to user command."""
        user_id = UUID(command.user_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await uow.assignments.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await uow.assignments.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Check if already assigned
        if await uow.assignments.user_has_direct_permission(user_id, permission_id):
            return False  # Already assigned

        # Assign permission
        await uow.assignments.assign_permission_to_user(user_id, permission_id)

        uow.add_event(
            PermissionAssignedToUser(
                user_id=command.user_id,
                permission_id=command.permission_id,
            )
        )

        return True


class RemovePermissionFromUserHandler:
    """Handler for RemovePermissionFromUserCommand."""

    async def handle(
        self, command: RemovePermissionFromUserCommand, uow: IIamUnitOfWork
    ) -> bool:
        """Execute the remove permission from user command."""
        user_id = UUID(command.user_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await uow.assignments.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await uow.assignments.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Remove permission
        removed = await uow.assignments.remove_permission_from_user(
            user_id, permission_id
        )

        if removed:
            uow.add_event(
                PermissionRemovedFromUser(
                    user_id=command.user_id,
                    permission_id=command.permission_id,
                )
            )

        return removed


class AssignPermissionToRoleHandler:
    """Handler for AssignPermissionToRoleCommand."""

    async def handle(
        self, command: AssignPermissionToRoleCommand, uow: IIamUnitOfWork
    ) -> bool:
        """Execute the assign permission to role command."""
        role_id = UUID(command.role_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await uow.assignments.role_exists(role_id):
            raise RoleNotFound(command.role_id)
        if not await uow.assignments.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Check if already assigned
        if await uow.assignments.role_has_permission(role_id, permission_id):
            return False  # Already assigned

        # Assign permission
        await uow.assignments.assign_permission_to_role(role_id, permission_id)

        uow.add_event(
            PermissionAssignedToRole(
                role_id=command.role_id,
                permission_id=command.permission_id,
            )
        )

        return True


class RemovePermissionFromRoleHandler:
    """Handler for RemovePermissionFromRoleCommand."""

    async def handle(
        self, command: RemovePermissionFromRoleCommand, uow: IIamUnitOfWork
    ) -> bool:
        """Execute the remove permission from role command."""
        role_id = UUID(command.role_id)
        permission_id = UUID(command.permission_id)

        # Verify entities exist
        if not await uow.assignments.role_exists(role_id):
            raise RoleNotFound(command.role_id)
        if not await uow.assignments.permission_exists(permission_id):
            raise PermissionNotFound(command.permission_id)

        # Remove permission
        removed = await uow.assignments.remove_permission_from_role(
            role_id, permission_id
        )

        if removed:
            uow.add_event(
                PermissionRemovedFromRole(
                    role_id=command.role_id,
                    permission_id=command.permission_id,
                )
            )

        return removed
