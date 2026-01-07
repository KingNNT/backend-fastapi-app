"""Permission write repository implementation for PostgreSQL."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.aggregates.permission import PermissionAggregate
from app.core.domain.value_objects.permission_name import PermissionName
from app.infrastructure.persistence.postgresql.mappers.permission import (
    PermissionMapper,
)
from app.infrastructure.persistence.postgresql.models.permission import PermissionModel


class PostgresPermissionWriteRepository:
    """PostgreSQL implementation of permission write repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = PermissionMapper()

    async def save(self, aggregate: PermissionAggregate) -> None:
        """Save a permission aggregate (create or update)."""
        permission_id = aggregate.id.value

        # Check if permission exists
        stmt = select(PermissionModel).where(PermissionModel.id == permission_id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing permission
            self._mapper.update_model(existing, aggregate)
            await self._session.flush()
        else:
            # Create new permission
            model = self._mapper.to_model(aggregate)
            self._session.add(model)
            await self._session.flush()

    async def delete(self, aggregate: PermissionAggregate) -> None:
        """Delete a permission aggregate (actually performs soft delete via save)."""
        await self.save(aggregate)

    async def exists_by_name(self, name: PermissionName) -> bool:
        """Check if a permission with the given name exists."""
        stmt = select(PermissionModel).where(
            PermissionModel.name == str(name),
            PermissionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
