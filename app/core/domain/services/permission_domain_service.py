"""Permission domain service - cross-entity domain logic."""

from app.core.domain.exceptions.permission import PermissionAlreadyExists
from app.core.domain.repositories.permission import IPermissionReadRepository
from app.core.domain.value_objects.permission_name import PermissionName


class PermissionDomainService:
    """Domain service for permission-related cross-entity operations.

    Contains domain logic that doesn't naturally fit in an entity or aggregate.
    This service is stateless - all methods receive dependencies as parameters.
    """

    @staticmethod
    async def ensure_name_unique(
        name: PermissionName,
        permission_read_repo: IPermissionReadRepository,
        exclude_permission_id: str | None = None,
    ) -> None:
        """Ensure the permission name is unique across all permissions.

        Args:
            name: The permission name to check.
            permission_read_repo: Repository for reading permission data.
            exclude_permission_id: Optional permission ID to exclude (for updates).

        Raises:
            PermissionAlreadyExists: If permission name is already taken.
        """
        existing_permission = await permission_read_repo.get_by_name(name)
        if existing_permission is not None:
            if (
                exclude_permission_id is None
                or existing_permission.id_str != exclude_permission_id
            ):
                raise PermissionAlreadyExists(str(name))

    @staticmethod
    async def validate_new_permission(
        name: PermissionName,
        permission_read_repo: IPermissionReadRepository,
    ) -> None:
        """Validate a new permission can be created with the given name.

        Args:
            name: The name for the new permission.
            permission_read_repo: Repository for reading permission data.

        Raises:
            PermissionAlreadyExists: If permission name is already taken.
        """
        await PermissionDomainService.ensure_name_unique(name, permission_read_repo)

    @staticmethod
    async def validate_permission_update(
        permission_id: str,
        permission_read_repo: IPermissionReadRepository,
        name: PermissionName | None = None,
    ) -> None:
        """Validate permission update doesn't violate uniqueness constraints.

        Args:
            permission_id: The ID of the permission being updated.
            permission_read_repo: Repository for reading permission data.
            name: Optional new name to validate.

        Raises:
            PermissionAlreadyExists: If new name is already taken.
        """
        if name is not None:
            await PermissionDomainService.ensure_name_unique(
                name, permission_read_repo, exclude_permission_id=permission_id
            )
