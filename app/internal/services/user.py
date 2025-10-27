from datetime import datetime, timezone
from uuid import UUID

from beanie import PydanticObjectId

from app.internal.dtos import UserCreate, UserResponse, UserUpdate
from app.internal.models.no_sql import User
from app.internal.repositories import UserRepository
from app.internal.exceptions import UserAlreadyExists, UserNotFound


class UserService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.repository = UserRepository()
            UserService._initialized = True

    async def create_user(
        self, user_data: UserCreate, created_by: UUID | None = None
    ) -> UserResponse:
        # Check if email already exists
        if await self.repository.email_exists(user_data.email):
            raise UserAlreadyExists("email", user_data.email)

        # Check if username already exists
        if await self.repository.username_exists(user_data.username):
            raise UserAlreadyExists("username", user_data.username)

        # Create user (in real app, hash password properly)
        now = datetime.now(timezone.utc)
        user = User(  # type: ignore
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            password=f"hashed_{user_data.password}",  # Simplified for demo
        )

        # Set audit fields
        user.created_at = now
        user.created_by = created_by
        user.updated_at = now
        user.updated_by = created_by

        created_user = await self.repository.create(user)
        return UserResponse(**created_user.model_dump())

    async def get_user(self, user_id: PydanticObjectId) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFound(str(user_id))

        return UserResponse(**user.model_dump())

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        email: str | None = None,
        username: str | None = None,
    ) -> list[UserResponse]:
        users = await self.repository.get_all(
            skip=skip, limit=limit, email=email, username=username
        )
        return [UserResponse(**user.model_dump()) for user in users]

    async def update_user(
        self,
        user_id: PydanticObjectId,
        user_data: UserUpdate,
        updated_by: UUID | None = None,
    ) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFound(str(user_id))

        # Check if email already exists (if being updated)
        if user_data.email and await self.repository.email_exists(
            user_data.email, exclude_user_id=user_id
        ):
            raise UserAlreadyExists("email", user_data.email)

        # Check if username already exists (if being updated)
        if user_data.username and await self.repository.username_exists(
            user_data.username, exclude_user_id=user_id
        ):
            raise UserAlreadyExists("username", user_data.username)

        # Update user fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        # Update audit fields
        user.updated_at = datetime.now(timezone.utc)
        user.updated_by = updated_by

        updated_user = await self.repository.update(user)
        return UserResponse(**updated_user.model_dump())

    async def delete_user(
        self, user_id: PydanticObjectId, deleted_by: UUID | None = None
    ) -> bool:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFound(str(user_id))

        # Soft delete the user
        user.soft_delete(deleted_by)
        await self.repository.delete(user)
        return True


def get_user_service() -> UserService:
    """
    Dependency function to provide UserService instance.
    Since UserService is implemented as a singleton, this will always
    return the same instance.
    """
    return UserService()
