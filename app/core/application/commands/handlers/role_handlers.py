"""Role command handlers - execute role write operations."""

from uuid import UUID

from app.core.application.commands.role.create_role import CreateRoleCommand
from app.core.application.commands.role.delete_role import DeleteRoleCommand
from app.core.application.commands.role.update_role import UpdateRoleCommand
from app.core.application.interfaces.event_bus import IEventBus
from app.core.domain.aggregates.role import RoleAggregate
from app.core.domain.exceptions.role import RoleAlreadyExists, RoleNotFound
from app.core.domain.repositories.role import IRoleRepository
from app.core.domain.value_objects.role_id import RoleId
from app.core.domain.value_objects.role_name import RoleName


class CreateRoleHandler:
    """Handler for CreateRoleCommand."""

    def __init__(
        self,
        repository: IRoleRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: CreateRoleCommand) -> str:
        """Execute the create role command and return role ID."""
        name = RoleName(command.name)

        # Check if role with same name already exists
        existing = await self._repository.get_by_name(name)
        if existing is not None:
            raise RoleAlreadyExists(command.name)

        # Create aggregate
        aggregate = RoleAggregate.create(
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


class UpdateRoleHandler:
    """Handler for UpdateRoleCommand."""

    def __init__(
        self,
        repository: IRoleRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: UpdateRoleCommand) -> str:
        """Execute the update role command and return role ID."""
        # Get existing role
        role_id = RoleId.from_string(command.role_id)
        aggregate = await self._repository.get_by_id(role_id)
        if aggregate is None:
            raise RoleNotFound(command.role_id)

        # Update name if provided
        if command.name is not None:
            new_name = RoleName(command.name)
            # Check uniqueness (exclude current role)
            existing = await self._repository.get_by_name(new_name)
            if existing is not None and existing.id_str != command.role_id:
                raise RoleAlreadyExists(command.name)
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


class DeleteRoleHandler:
    """Handler for DeleteRoleCommand."""

    def __init__(
        self,
        repository: IRoleRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: DeleteRoleCommand) -> bool:
        """Execute the delete role command."""
        # Get existing role
        role_id = RoleId.from_string(command.role_id)
        aggregate = await self._repository.get_by_id(role_id)
        if aggregate is None:
            raise RoleNotFound(command.role_id)

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
