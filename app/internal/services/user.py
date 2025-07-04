from datetime import datetime, timezone
from uuid import UUID

from beanie import PydanticObjectId

from app.internal.dtos.user import UserCreate, UserResponse, UserUpdate
from app.internal.models.user import User
from app.internal.repositories.user import UserRepository
from app.exceptions import UserAlreadyExists, UserNotFound


class UserService:
    def __init__(self):
        self.repository = UserRepository()

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
            password_hash=f"hashed_{user_data.password}",  # Simplified for demo
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

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        users = await self.repository.get_all(skip=skip, limit=limit)
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

    async def get_user_by_email(self, email: str) -> UserResponse:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFound(email=email)
        return UserResponse(**user.model_dump())

    async def get_user_by_username(self, username: str) -> UserResponse:
        user = await self.repository.get_by_username(username)
        if not user:
            raise UserNotFound(f"username '{username}'")
        return UserResponse(**user.model_dump())
