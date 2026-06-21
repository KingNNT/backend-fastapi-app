"""User repository interface - defines data access contract."""

from typing import Optional, Protocol

from app.iam.domain.user.aggregate import UserAggregate
from app.iam.domain.user.value_objects import Email, Username
from app.shared.domain.ids.user_id import UserId


class IUserWriteRepository(Protocol):
    """
    Repository interface for user write operations (Command side).
    Implementations will be in the infrastructure layer.
    """

    async def save(self, aggregate: UserAggregate) -> None:
        """Save a user aggregate (create or update)."""
        ...

    async def delete(self, aggregate: UserAggregate) -> None:
        """Delete a user aggregate."""
        ...

    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user with the given email exists."""
        ...

    async def exists_by_username(self, username: Username) -> bool:
        """Check if a user with the given username exists."""
        ...


class IUserReadRepository(Protocol):
    """
    Repository interface for user read operations (Query side).
    Implementations will be in the infrastructure layer.
    """

    async def get_by_id(self, user_id: UserId) -> Optional[UserAggregate]:
        """Get a user by ID."""
        ...

    async def get_by_email(self, email: Email) -> Optional[UserAggregate]:
        """Get a user by email."""
        ...

    async def get_by_username(self, username: Username) -> Optional[UserAggregate]:
        """Get a user by username."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[UserAggregate]:
        """List all users with pagination."""
        ...

    async def count(self, include_deleted: bool = False) -> int:
        """Count total users."""
        ...
