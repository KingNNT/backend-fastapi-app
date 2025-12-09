"""User read repository implementation for PostgreSQL."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.application.read_models.user_read_model import UserReadModel
from app.core.domain.aggregates.user import UserAggregate
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.user_id import UserId
from app.core.domain.value_objects.username import Username
from app.infrastructure.persistence.postgresql.mappers.user import UserMapper
from app.infrastructure.persistence.postgresql.models.user import UserModel


class PostgresUserReadRepository:
    """PostgreSQL implementation of user read repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = UserMapper()

    async def get_by_id(self, user_id: UserId) -> Optional[UserAggregate]:
        """Get a user by ID."""
        stmt = select(UserModel).where(
            UserModel.id == user_id.value,
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_aggregate(model)

    async def get_by_email(self, email: Email) -> Optional[UserAggregate]:
        """Get a user by email."""
        stmt = select(UserModel).where(
            UserModel.email == str(email),
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_aggregate(model)

    async def get_by_username(self, username: Username) -> Optional[UserAggregate]:
        """Get a user by username."""
        stmt = select(UserModel).where(
            UserModel.username == str(username),
            UserModel.deleted_at.is_(None),
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
    ) -> list[UserAggregate]:
        """List all users with pagination."""
        stmt = select(UserModel)
        if not include_deleted:
            stmt = stmt.where(UserModel.deleted_at.is_(None))
        stmt = stmt.offset(skip).limit(limit).order_by(UserModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_aggregate(model) for model in models]

    async def count(self, include_deleted: bool = False) -> int:
        """Count total users."""
        stmt = select(func.count(UserModel.id))
        if not include_deleted:
            stmt = stmt.where(UserModel.deleted_at.is_(None))

        result = await self._session.execute(stmt)
        return result.scalar_one()


class PostgresUserReadModelRepository:
    """PostgreSQL implementation of user read model repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = UserMapper()

    async def get_by_id(self, user_id: str) -> Optional[UserReadModel]:
        """Get user read model by ID."""
        try:
            uuid_id = UUID(user_id)
        except ValueError:
            return None

        stmt = select(UserModel).where(
            UserModel.id == uuid_id,
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_read_model(model)

    async def get_by_email(self, email: str) -> Optional[UserReadModel]:
        """Get user read model by email."""
        stmt = select(UserModel).where(
            UserModel.email == email,
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._mapper.to_read_model(model)

    async def get_by_username(self, username: str) -> Optional[UserReadModel]:
        """Get user read model by username."""
        stmt = select(UserModel).where(
            UserModel.username == username,
            UserModel.deleted_at.is_(None),
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
    ) -> list[UserReadModel]:
        """List user read models with pagination."""
        stmt = select(UserModel)
        if not include_deleted:
            stmt = stmt.where(UserModel.deleted_at.is_(None))
        stmt = stmt.offset(skip).limit(limit).order_by(UserModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_read_model(model) for model in models]
