"""Permission read repository implementation for PostgreSQL."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.iam.application.read_models.permission_read_model import PermissionReadModel
from app.iam.domain.permission.aggregate import PermissionAggregate
from app.iam.domain.permission.value_objects import PermissionName
from app.iam.infrastructure.persistence.postgresql.mappers.permission import (
    PermissionMapper,
)
from app.iam.infrastructure.persistence.postgresql.models.permission import (
    PermissionModel,
)
from app.shared.domain.ids.permission_id import PermissionId


class PostgresPermissionReadRepository:
    """PostgreSQL implementation of permission read repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = PermissionMapper()

    async def get_by_id(
        self, permission_id: PermissionId
    ) -> Optional[PermissionAggregate]:
        """Get a permission by ID."""
        stmt = select(PermissionModel).where(
            PermissionModel.id == permission_id.value,
            PermissionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_aggregate(model)

    async def get_by_name(self, name: PermissionName) -> Optional[PermissionAggregate]:
        """Get a permission by name."""
        stmt = select(PermissionModel).where(
            PermissionModel.name == str(name),
            PermissionModel.deleted_at.is_(None),
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
    ) -> list[PermissionAggregate]:
        """List all permissions with pagination."""
        stmt = select(PermissionModel)
        if not include_deleted:
            stmt = stmt.where(PermissionModel.deleted_at.is_(None))
        stmt = (
            stmt.offset(skip).limit(limit).order_by(PermissionModel.created_at.desc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_aggregate(model) for model in models]

    async def count(self, include_deleted: bool = False) -> int:
        """Count total permissions."""
        stmt = select(func.count(PermissionModel.id))
        if not include_deleted:
            stmt = stmt.where(PermissionModel.deleted_at.is_(None))

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_by_ids(self, permission_ids: list[UUID]) -> list[PermissionAggregate]:
        """Get permissions by list of IDs."""
        if not permission_ids:
            return []

        stmt = select(PermissionModel).where(
            PermissionModel.id.in_(permission_ids),
            PermissionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_aggregate(model) for model in models]


class PostgresPermissionReadModelRepository:
    """PostgreSQL implementation of permission read model repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = PermissionMapper()

    async def get_by_id(self, permission_id: str) -> Optional[PermissionReadModel]:
        """Get permission read model by ID."""
        try:
            uuid_id = UUID(permission_id)
        except ValueError:
            return None

        stmt = select(PermissionModel).where(
            PermissionModel.id == uuid_id,
            PermissionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_read_model(model)

    async def get_by_name(self, name: str) -> Optional[PermissionReadModel]:
        """Get permission read model by name."""
        stmt = select(PermissionModel).where(
            PermissionModel.name == name,
            PermissionModel.deleted_at.is_(None),
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
    ) -> list[PermissionReadModel]:
        """List permission read models with pagination."""
        stmt = select(PermissionModel)
        if not include_deleted:
            stmt = stmt.where(PermissionModel.deleted_at.is_(None))
        stmt = (
            stmt.offset(skip).limit(limit).order_by(PermissionModel.created_at.desc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_read_model(model) for model in models]

    async def get_by_ids(self, permission_ids: list[str]) -> list[PermissionReadModel]:
        """Get permission read models by IDs."""
        if not permission_ids:
            return []

        uuid_ids = []
        for permission_id in permission_ids:
            try:
                uuid_ids.append(UUID(permission_id))
            except ValueError:
                continue

        if not uuid_ids:
            return []

        stmt = select(PermissionModel).where(
            PermissionModel.id.in_(uuid_ids),
            PermissionModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_read_model(model) for model in models]
