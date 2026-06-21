"""Role write repository implementation for PostgreSQL."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.iam.domain.role.aggregate import RoleAggregate
from app.iam.domain.role.value_objects import RoleName
from app.infrastructure.persistence.postgresql.mappers.role import RoleMapper
from app.infrastructure.persistence.postgresql.models.role import RoleModel


class PostgresRoleWriteRepository:
    """PostgreSQL implementation of role write repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = RoleMapper()

    async def save(self, aggregate: RoleAggregate) -> None:
        """Save a role aggregate (create or update)."""
        role_id = aggregate.id.value

        # Check if role exists
        stmt = select(RoleModel).where(RoleModel.id == role_id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing role
            self._mapper.update_model(existing, aggregate)
            await self._session.flush()
        else:
            # Create new role
            model = self._mapper.to_model(aggregate)
            self._session.add(model)
            await self._session.flush()

    async def delete(self, aggregate: RoleAggregate) -> None:
        """Delete a role aggregate (actually performs soft delete via save)."""
        await self.save(aggregate)

    async def exists_by_name(self, name: RoleName) -> bool:
        """Check if a role with the given name exists."""
        stmt = select(RoleModel).where(
            RoleModel.name == str(name),
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
