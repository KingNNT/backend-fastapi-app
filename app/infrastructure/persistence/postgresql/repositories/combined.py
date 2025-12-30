"""Combined repositories that wrap both read and write operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.postgresql.repositories.permission_read import (
    PostgresPermissionReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.permission_write import (
    PostgresPermissionWriteRepository,
)
from app.infrastructure.persistence.postgresql.repositories.role_read import (
    PostgresRoleReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.role_write import (
    PostgresRoleWriteRepository,
)
from app.infrastructure.persistence.postgresql.repositories.user_read import (
    PostgresUserReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.user_write import (
    PostgresUserWriteRepository,
)


class CombinedUserRepository:
    """Combined repository that implements both read and write operations for users."""

    def __init__(self, session: AsyncSession) -> None:
        self._write_repo = PostgresUserWriteRepository(session)
        self._read_repo = PostgresUserReadRepository(session)

    # Write operations
    async def save(self, aggregate):
        return await self._write_repo.save(aggregate)

    async def delete(self, aggregate):
        return await self._write_repo.delete(aggregate)

    async def exists_by_email(self, email):
        return await self._write_repo.exists_by_email(email)

    async def exists_by_username(self, username):
        return await self._write_repo.exists_by_username(username)

    # Read operations
    async def get_by_id(self, user_id):
        return await self._read_repo.get_by_id(user_id)

    async def get_by_email(self, email):
        return await self._read_repo.get_by_email(email)

    async def get_by_username(self, username):
        return await self._read_repo.get_by_username(username)

    async def list_all(self, skip=0, limit=100, include_deleted=False):
        return await self._read_repo.list_all(skip, limit, include_deleted)

    async def count(self, include_deleted=False):
        return await self._read_repo.count(include_deleted)


class CombinedRoleRepository:
    """Combined repository that implements both read and write operations for roles."""

    def __init__(self, session: AsyncSession) -> None:
        self._write_repo = PostgresRoleWriteRepository(session)
        self._read_repo = PostgresRoleReadRepository(session)

    # Write operations
    async def save(self, aggregate):
        return await self._write_repo.save(aggregate)

    async def delete(self, aggregate):
        return await self._write_repo.delete(aggregate)

    async def exists_by_name(self, name):
        return await self._write_repo.exists_by_name(name)

    # Read operations
    async def get_by_id(self, role_id):
        return await self._read_repo.get_by_id(role_id)

    async def get_by_name(self, name):
        return await self._read_repo.get_by_name(name)

    async def list_all(self, skip=0, limit=100, include_deleted=False):
        return await self._read_repo.list_all(skip, limit, include_deleted)

    async def count(self, include_deleted=False):
        return await self._read_repo.count(include_deleted)


class CombinedPermissionRepository:
    """Combined repo that implements both read and write operations for permissions."""

    def __init__(self, session: AsyncSession) -> None:
        self._write_repo = PostgresPermissionWriteRepository(session)
        self._read_repo = PostgresPermissionReadRepository(session)

    # Write operations
    async def save(self, aggregate):
        return await self._write_repo.save(aggregate)

    async def delete(self, aggregate):
        return await self._write_repo.delete(aggregate)

    async def exists_by_name(self, name):
        return await self._write_repo.exists_by_name(name)

    # Read operations
    async def get_by_id(self, permission_id):
        return await self._read_repo.get_by_id(permission_id)

    async def get_by_name(self, name):
        return await self._read_repo.get_by_name(name)

    async def list_all(self, skip=0, limit=100, include_deleted=False):
        return await self._read_repo.list_all(skip, limit, include_deleted)

    async def count(self, include_deleted=False):
        return await self._read_repo.count(include_deleted)
