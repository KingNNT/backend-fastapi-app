"""Permission command handlers - execute permission write operations."""

from uuid import UUID

from app.core.application.commands.permission.create_permission import (
    CreatePermissionCommand,
)
from app.core.application.commands.permission.delete_permission import (
    DeletePermissionCommand,
)
from app.core.application.commands.permission.update_permission import (
    UpdatePermissionCommand,
)
from app.core.application.interfaces import IUnitOfWork
from app.core.domain.aggregates.permission import PermissionAggregate
from app.core.domain.exceptions.permission import PermissionNotFound
from app.core.domain.services import PermissionDomainService
from app.core.domain.value_objects.permission_id import PermissionId
from app.core.domain.value_objects.permission_name import PermissionName


class CreatePermissionHandler:
    """Handler for CreatePermissionCommand.

    Uses Unit of Work for transaction management and repository access.
    Delegates domain validation to PermissionDomainService.
    """

    def __init__(self) -> None:
        """Initialize handler (no dependencies needed)."""
        pass

    async def handle(self, command: CreatePermissionCommand, uow: IUnitOfWork) -> str:
        """Execute the create permission command and return permission ID.

        Args:
            command: The create permission command containing permission data.
            uow: Unit of Work for transaction management.

        Returns:
            The created permission's ID as string.

        Raises:
            PermissionAlreadyExists: If permission name already exists.
        """
        name = PermissionName(command.name)

        # Validate uniqueness via domain service
        await PermissionDomainService.validate_new_permission(
            name, uow.permissions_read
        )

        # Create aggregate
        aggregate = PermissionAggregate.create(
            name=name,
            description=command.description,
        )

        # Persist via UoW
        await uow.permissions.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return aggregate.id_str


class UpdatePermissionHandler:
    """Handler for UpdatePermissionCommand.

    Uses Unit of Work for transaction management and repository access.
    Delegates domain validation to PermissionDomainService.
    """

    def __init__(self) -> None:
        """Initialize handler (no dependencies needed)."""
        pass

    async def handle(self, command: UpdatePermissionCommand, uow: IUnitOfWork) -> str:
        """Execute the update permission command and return permission ID.

        Args:
            command: The update permission command containing update data.
            uow: Unit of Work for transaction management.

        Returns:
            The updated permission's ID as string.

        Raises:
            PermissionNotFound: If permission doesn't exist.
            PermissionAlreadyExists: If new name already taken.
        """
        # Get existing permission
        permission_id = PermissionId.from_string(command.permission_id)
        aggregate = await uow.permissions_read.get_by_id(permission_id)
        if aggregate is None:
            raise PermissionNotFound(command.permission_id)

        # Parse new name if provided
        new_name = PermissionName(command.name) if command.name else None

        # Validate uniqueness via domain service
        await PermissionDomainService.validate_permission_update(
            permission_id=command.permission_id,
            permission_read_repo=uow.permissions_read,
            name=new_name,
        )

        # Apply updates
        if new_name is not None:
            aggregate.update_name(new_name)

        if command.description is not None:
            aggregate.update_description(command.description)

        # Persist via UoW
        await uow.permissions.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return aggregate.id_str


class DeletePermissionHandler:
    """Handler for DeletePermissionCommand.

    Uses Unit of Work for transaction management and repository access.
    """

    def __init__(self) -> None:
        """Initialize handler (no dependencies needed)."""
        pass

    async def handle(self, command: DeletePermissionCommand, uow: IUnitOfWork) -> bool:
        """Execute the delete permission command.

        Args:
            command: The delete permission command.
            uow: Unit of Work for transaction management.

        Returns:
            True if deletion was successful.

        Raises:
            PermissionNotFound: If permission doesn't exist.
        """
        # Get existing permission
        permission_id = PermissionId.from_string(command.permission_id)
        aggregate = await uow.permissions_read.get_by_id(permission_id)
        if aggregate is None:
            raise PermissionNotFound(command.permission_id)

        # Soft delete
        deleted_by = UUID(command.deleted_by) if command.deleted_by else None
        aggregate.soft_delete(deleted_by=deleted_by)

        # Persist via UoW
        await uow.permissions.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return True
