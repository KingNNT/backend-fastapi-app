"""User write repository implementation for PostgreSQL."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.domain.aggregates.user import UserAggregate
from app.core.domain.value_objects.email import Email
from app.core.domain.value_objects.username import Username
from app.infrastructure.persistence.postgresql.mappers.user import UserMapper
from app.infrastructure.persistence.postgresql.models.user import UserModel


class PostgresUserWriteRepository:
    """PostgreSQL implementation of user write repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = UserMapper()

    async def save(self, aggregate: UserAggregate) -> None:
        """Save a user aggregate (create or update)."""
        user_id = aggregate.id.value

        # Check if user exists
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing user
            self._mapper.update_model(existing, aggregate)
            await self._session.commit()
        else:
            # Create new user
            model = self._mapper.to_model(aggregate)
            self._session.add(model)
            await self._session.commit()

    async def delete(self, aggregate: UserAggregate) -> None:
        """Delete a user aggregate (actually performs soft delete via save)."""
        await self.save(aggregate)

    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user with the given email exists."""
        stmt = select(UserModel).where(
            UserModel.email == str(email),
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: Username) -> bool:
        """Check if a user with the given username exists."""
        stmt = select(UserModel).where(
            UserModel.username == str(username),
            UserModel.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
