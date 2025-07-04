from beanie import PydanticObjectId
from beanie.operators import And

from app.internal.models.user import User


class UserRepository:
    """Repository pattern for User operations with MongoDB."""

    async def create(self, user: User) -> User:
        """Create a new user."""
        return await user.create()

    async def get_by_id(self, user_id: PydanticObjectId) -> User | None:
        """Get user by ID, excluding soft-deleted users."""
        return await User.find_one(And(User.id == user_id, User.deleted_at is None))

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email, excluding soft-deleted users."""
        return await User.find_one(And(User.email == email, User.deleted_at is None))

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username, excluding soft-deleted users."""
        return await User.find_one(
            And(User.username == username, User.deleted_at is None)
        )

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users with pagination."""
        return (
            await User.find(User.deleted_at is None).skip(skip).limit(limit).to_list()
        )

    async def update(self, user: User) -> User:
        """Update user."""
        return await user.save()

    async def delete(self, user: User) -> User:
        """Soft delete user."""
        return await user.save()

    async def email_exists(
        self, email: str, exclude_user_id: PydanticObjectId | None = None
    ) -> bool:
        """Check if email exists, excluding soft-deleted users and optionally a specific user."""
        query = And(User.email == email, User.deleted_at is None)
        if exclude_user_id:
            query = And(query, User.id != exclude_user_id)

        user = await User.find_one(query)
        return user is not None

    async def username_exists(
        self, username: str, exclude_user_id: PydanticObjectId | None = None
    ) -> bool:
        """Check if username exists, excluding soft-deleted users and optionally a specific user."""
        query = And(User.username == username, User.deleted_at is None)
        if exclude_user_id:
            query = And(query, User.id != exclude_user_id)

        user = await User.find_one(query)
        return user is not None
