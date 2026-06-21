"""Role command handlers - execute role write operations."""

from uuid import UUID

from app.iam.application.commands.role.create_role import CreateRoleCommand
from app.iam.application.commands.role.delete_role import DeleteRoleCommand
from app.iam.application.commands.role.update_role import UpdateRoleCommand
from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork
from app.iam.domain.role.aggregate import RoleAggregate
from app.iam.domain.role.domain_service import RoleDomainService
from app.iam.domain.role.exceptions import RoleNotFound
from app.iam.domain.role.value_objects import RoleName
from app.shared.domain.ids.role_id import RoleId


class CreateRoleHandler:
    """Handler for CreateRoleCommand.

    Uses Unit of Work for transaction management and repository access.
    Delegates domain validation to RoleDomainService.
    """

    def __init__(self) -> None:
        """Initialize handler (no dependencies needed)."""
        pass

    async def handle(self, command: CreateRoleCommand, uow: IIamUnitOfWork) -> str:
        """Execute the create role command and return role ID.

        Args:
            command: The create role command containing role data.
            uow: Unit of Work for transaction management.

        Returns:
            The created role's ID as string.

        Raises:
            RoleAlreadyExists: If role name already exists.
        """
        name = RoleName(command.name)

        # Validate uniqueness via domain service
        await RoleDomainService.validate_new_role(name, uow.roles_read)

        # Create aggregate
        aggregate = RoleAggregate.create(
            name=name,
            description=command.description,
        )

        # Persist via UoW
        await uow.roles.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return aggregate.id_str


class UpdateRoleHandler:
    """Handler for UpdateRoleCommand.

    Uses Unit of Work for transaction management and repository access.
    Delegates domain validation to RoleDomainService.
    """

    def __init__(self) -> None:
        """Initialize handler (no dependencies needed)."""
        pass

    async def handle(self, command: UpdateRoleCommand, uow: IIamUnitOfWork) -> str:
        """Execute the update role command and return role ID.

        Args:
            command: The update role command containing update data.
            uow: Unit of Work for transaction management.

        Returns:
            The updated role's ID as string.

        Raises:
            RoleNotFound: If role doesn't exist.
            RoleAlreadyExists: If new name already taken.
        """
        # Get existing role
        role_id = RoleId.from_string(command.role_id)
        aggregate = await uow.roles_read.get_by_id(role_id)
        if aggregate is None:
            raise RoleNotFound(command.role_id)

        # Parse new name if provided
        new_name = RoleName(command.name) if command.name else None

        # Validate uniqueness via domain service
        await RoleDomainService.validate_role_update(
            role_id=command.role_id,
            role_read_repo=uow.roles_read,
            name=new_name,
        )

        # Apply updates
        if new_name is not None:
            aggregate.update_name(new_name)

        if command.description is not None:
            aggregate.update_description(command.description)

        # Persist via UoW
        await uow.roles.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return aggregate.id_str


class DeleteRoleHandler:
    """Handler for DeleteRoleCommand.

    Uses Unit of Work for transaction management and repository access.
    """

    def __init__(self) -> None:
        """Initialize handler (no dependencies needed)."""
        pass

    async def handle(self, command: DeleteRoleCommand, uow: IIamUnitOfWork) -> bool:
        """Execute the delete role command.

        Args:
            command: The delete role command.
            uow: Unit of Work for transaction management.

        Returns:
            True if deletion was successful.

        Raises:
            RoleNotFound: If role doesn't exist.
        """
        # Get existing role
        role_id = RoleId.from_string(command.role_id)
        aggregate = await uow.roles_read.get_by_id(role_id)
        if aggregate is None:
            raise RoleNotFound(command.role_id)

        # Soft delete
        deleted_by = UUID(command.deleted_by) if command.deleted_by else None
        aggregate.soft_delete(deleted_by=deleted_by)

        # Persist via UoW
        await uow.roles.save(aggregate)

        # Collect events (will be published after commit)
        uow.collect_events(aggregate)

        return True
