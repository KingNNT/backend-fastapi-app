# ruff: noqa: E711
from beanie import PydanticObjectId

from app.internal.models.no_sql import User


class UserRepository:
    """Repository pattern for User operations with MongoDB."""

    async def create(self, user: User) -> User:
        """Create a new user."""
        return await user.create()

    async def get_by_id(self, user_id: PydanticObjectId) -> User | None:
        """Get user by ID, excluding soft-deleted users."""
        return await User.find_one(User.id == user_id, User.deleted_at == None)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        email: str | None = None,
        username: str | None = None,
    ) -> list[User]:
        """Get all active users with pagination and optional filtering."""
        # Build filter conditions
        conditions = [User.deleted_at == None]

        if email:
            conditions.append(User.email == email)

        if username:
            conditions.append(User.username == username)

        return await User.find(*conditions).skip(skip).limit(limit).to_list()

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
        if exclude_user_id:
            user = await User.find_one(
                User.email == email, User.deleted_at == None, User.id != exclude_user_id
            )
        else:
            user = await User.find_one(User.email == email, User.deleted_at == None)

        return user is not None

    async def username_exists(
        self, username: str, exclude_user_id: PydanticObjectId | None = None
    ) -> bool:
        """Check if username exists, excluding soft-deleted users and optionally a specific user."""
        if exclude_user_id:
            user = await User.find_one(
                User.username == username,
                User.deleted_at == None,
                User.id != exclude_user_id,
            )
        else:
            user = await User.find_one(
                User.username == username, User.deleted_at == None
            )

        return user is not None
