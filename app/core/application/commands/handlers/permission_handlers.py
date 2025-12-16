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
from app.core.application.interfaces.event_bus import IEventBus
from app.core.domain.aggregates.permission import PermissionAggregate
from app.core.domain.exceptions.permission import (
    PermissionAlreadyExists,
    PermissionNotFound,
)
from app.core.domain.repositories.permission import IPermissionRepository
from app.core.domain.value_objects.permission_id import PermissionId
from app.core.domain.value_objects.permission_name import PermissionName


class CreatePermissionHandler:
    """Handler for CreatePermissionCommand."""

    def __init__(
        self,
        repository: IPermissionRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: CreatePermissionCommand) -> str:
        """Execute the create permission command and return permission ID."""
        name = PermissionName(command.name)

        # Check if permission with same name already exists
        existing = await self._repository.get_by_name(name)
        if existing is not None:
            raise PermissionAlreadyExists(command.name)

        # Create aggregate
        aggregate = PermissionAggregate.create(
            name=name,
            description=command.description,
        )

        # Persist
        await self._repository.save(aggregate)

        # Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)
        aggregate.clear_events()

        return aggregate.id_str


class UpdatePermissionHandler:
    """Handler for UpdatePermissionCommand."""

    def __init__(
        self,
        repository: IPermissionRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: UpdatePermissionCommand) -> str:
        """Execute the update permission command and return permission ID."""
        # Get existing permission
        permission_id = PermissionId.from_string(command.permission_id)
        aggregate = await self._repository.get_by_id(permission_id)
        if aggregate is None:
            raise PermissionNotFound(command.permission_id)

        # Update name if provided
        if command.name is not None:
            new_name = PermissionName(command.name)
            # Check uniqueness (exclude current permission)
            existing = await self._repository.get_by_name(new_name)
            if existing is not None and existing.id_str != command.permission_id:
                raise PermissionAlreadyExists(command.name)
            aggregate.update_name(new_name)

        # Update description if provided
        if command.description is not None:
            aggregate.update_description(command.description)

        # Persist
        await self._repository.save(aggregate)

        # Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)
        aggregate.clear_events()

        return aggregate.id_str


class DeletePermissionHandler:
    """Handler for DeletePermissionCommand."""

    def __init__(
        self,
        repository: IPermissionRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: DeletePermissionCommand) -> bool:
        """Execute the delete permission command."""
        # Get existing permission
        permission_id = PermissionId.from_string(command.permission_id)
        aggregate = await self._repository.get_by_id(permission_id)
        if aggregate is None:
            raise PermissionNotFound(command.permission_id)

        # Soft delete
        deleted_by = UUID(command.deleted_by) if command.deleted_by else None
        aggregate.soft_delete(deleted_by=deleted_by)

        # Persist
        await self._repository.save(aggregate)

        # Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)
        aggregate.clear_events()

        return True
