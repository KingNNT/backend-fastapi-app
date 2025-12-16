"""Role read repository implementation for PostgreSQL."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.application.read_models.role_read_model import RoleReadModel
from app.core.domain.aggregates.role import RoleAggregate
from app.core.domain.value_objects.role_id import RoleId
from app.core.domain.value_objects.role_name import RoleName
from app.infrastructure.persistence.postgresql.mappers.role import RoleMapper
from app.infrastructure.persistence.postgresql.models.role import RoleModel


class PostgresRoleReadRepository:
    """PostgreSQL implementation of role read repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = RoleMapper()

    async def get_by_id(self, role_id: RoleId) -> Optional[RoleAggregate]:
        """Get a role by ID."""
        stmt = select(RoleModel).where(
            RoleModel.id == role_id.value,
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_aggregate(model)

    async def get_by_name(self, name: RoleName) -> Optional[RoleAggregate]:
        """Get a role by name."""
        stmt = select(RoleModel).where(
            RoleModel.name == str(name),
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_aggregate(model)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[RoleAggregate]:
        """List all roles with pagination."""
        stmt = select(RoleModel)
        if not include_deleted:
            stmt = stmt.where(RoleModel.deleted_at.is_(None))
        stmt = stmt.offset(skip).limit(limit).order_by(RoleModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_aggregate(model) for model in models]

    async def count(self, include_deleted: bool = False) -> int:
        """Count total roles."""
        stmt = select(func.count(RoleModel.id))
        if not include_deleted:
            stmt = stmt.where(RoleModel.deleted_at.is_(None))

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_by_ids(self, role_ids: list[UUID]) -> list[RoleAggregate]:
        """Get roles by list of IDs."""
        if not role_ids:
            return []

        stmt = select(RoleModel).where(
            RoleModel.id.in_(role_ids),
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_aggregate(model) for model in models]


class PostgresRoleReadModelRepository:
    """PostgreSQL implementation of role read model repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = RoleMapper()

    async def get_by_id(self, role_id: str) -> Optional[RoleReadModel]:
        """Get role read model by ID."""
        try:
            uuid_id = UUID(role_id)
        except ValueError:
            return None

        stmt = select(RoleModel).where(
            RoleModel.id == uuid_id,
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_read_model(model)

    async def get_by_name(self, name: str) -> Optional[RoleReadModel]:
        """Get role read model by name."""
        stmt = select(RoleModel).where(
            RoleModel.name == name,
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_read_model(model)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[RoleReadModel]:
        """List role read models with pagination."""
        stmt = select(RoleModel)
        if not include_deleted:
            stmt = stmt.where(RoleModel.deleted_at.is_(None))
        stmt = stmt.offset(skip).limit(limit).order_by(RoleModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_read_model(model) for model in models]

    async def get_by_ids(self, role_ids: list[str]) -> list[RoleReadModel]:
        """Get role read models by IDs."""
        if not role_ids:
            return []

        uuid_ids = []
        for role_id in role_ids:
            try:
                uuid_ids.append(UUID(role_id))
            except ValueError:
                continue

        if not uuid_ids:
            return []

        stmt = select(RoleModel).where(
            RoleModel.id.in_(uuid_ids),
            RoleModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_read_model(model) for model in models]
