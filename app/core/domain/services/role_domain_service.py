"""Role domain service - cross-entity domain logic."""

from app.core.domain.exceptions.role import RoleAlreadyExists
from app.core.domain.repositories.role import IRoleReadRepository
from app.core.domain.value_objects.role_name import RoleName


class RoleDomainService:
    """Domain service for role-related cross-entity operations.

    Contains domain logic that doesn't naturally fit in an entity or aggregate.
    This service is stateless - all methods receive dependencies as parameters.
    """

    @staticmethod
    async def ensure_name_unique(
        name: RoleName,
        role_read_repo: IRoleReadRepository,
        exclude_role_id: str | None = None,
    ) -> None:
        """Ensure the role name is unique across all roles.

        Args:
            name: The role name to check.
            role_read_repo: Repository for reading role data.
            exclude_role_id: Optional role ID to exclude (for updates).

        Raises:
            RoleAlreadyExists: If role name is already taken.
        """
        existing_role = await role_read_repo.get_by_name(name)
        if existing_role is not None:
            if exclude_role_id is None or existing_role.id_str != exclude_role_id:
                raise RoleAlreadyExists(str(name))

    @staticmethod
    async def validate_new_role(
        name: RoleName,
        role_read_repo: IRoleReadRepository,
    ) -> None:
        """Validate a new role can be created with the given name.

        Args:
            name: The name for the new role.
            role_read_repo: Repository for reading role data.

        Raises:
            RoleAlreadyExists: If role name is already taken.
        """
        await RoleDomainService.ensure_name_unique(name, role_read_repo)

    @staticmethod
    async def validate_role_update(
        role_id: str,
        role_read_repo: IRoleReadRepository,
        name: RoleName | None = None,
    ) -> None:
        """Validate role update doesn't violate uniqueness constraints.

        Args:
            role_id: The ID of the role being updated.
            role_read_repo: Repository for reading role data.
            name: Optional new name to validate.

        Raises:
            RoleAlreadyExists: If new name is already taken.
        """
        if name is not None:
            await RoleDomainService.ensure_name_unique(
                name, role_read_repo, exclude_role_id=role_id
            )
