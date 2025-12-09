"""User query handlers - execute user read operations."""

from typing import Optional, Protocol

from app.core.application.queries.user.get_user import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
)
from app.core.application.queries.user.list_users import ListUsersQuery
from app.core.application.read_models.user_read_model import UserReadModel


class IUserReadModelRepository(Protocol):
    """Interface for user read model repository."""

    async def get_by_id(self, user_id: str) -> Optional[UserReadModel]:
        """Get user read model by ID."""
        ...

    async def get_by_email(self, email: str) -> Optional[UserReadModel]:
        """Get user read model by email."""
        ...

    async def get_by_username(self, username: str) -> Optional[UserReadModel]:
        """Get user read model by username."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[UserReadModel]:
        """List user read models with pagination."""
        ...


class GetUserByIdHandler:
    """Handler for GetUserByIdQuery."""

    def __init__(self, repository: IUserReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetUserByIdQuery) -> Optional[UserReadModel]:
        """Execute the get user by ID query."""
        return await self._repository.get_by_id(query.user_id)


class GetUserByEmailHandler:
    """Handler for GetUserByEmailQuery."""

    def __init__(self, repository: IUserReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetUserByEmailQuery) -> Optional[UserReadModel]:
        """Execute the get user by email query."""
        return await self._repository.get_by_email(query.email)


class GetUserByUsernameHandler:
    """Handler for GetUserByUsernameQuery."""

    def __init__(self, repository: IUserReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetUserByUsernameQuery) -> Optional[UserReadModel]:
        """Execute the get user by username query."""
        return await self._repository.get_by_username(query.username)


class ListUsersHandler:
    """Handler for ListUsersQuery."""

    def __init__(self, repository: IUserReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListUsersQuery) -> list[UserReadModel]:
        """Execute the list users query."""
        return await self._repository.list_all(
            skip=query.skip,
            limit=query.limit,
            include_deleted=query.include_deleted,
        )
