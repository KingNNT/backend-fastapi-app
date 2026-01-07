"""Unit tests for command handlers."""

from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from app.core.application.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from app.core.application.commands.handlers import (
    CreateUserHandler,
    DeleteUserHandler,
    UpdateUserHandler,
)
from app.core.domain.aggregates import UserAggregate
from app.core.domain.exceptions import UserAlreadyExists, UserNotFound
from app.core.domain.value_objects import Email, Username


class TestCreateUserHandler:
    """Tests for CreateUserHandler.

    The handler now:
    - Takes only password_hasher in constructor
    - Receives UoW as parameter to handle() method
    - Uses uow.users for write operations
    - Uses uow.users_read for validation
    - Calls uow.collect_events() for event publishing
    """

    @pytest.fixture
    def handler(self, mock_password_hasher):
        """Create handler with mocked dependencies."""
        return CreateUserHandler(password_hasher=mock_password_hasher)

    @pytest.mark.asyncio
    async def test_create_user_success(self, handler, mock_unit_of_work):
        """Test successful user creation."""
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User",
        )

        user_id = await handler.handle(command, mock_unit_of_work)

        assert user_id is not None
        assert isinstance(user_id, str)
        mock_unit_of_work.users.save.assert_called_once()
        mock_unit_of_work.collect_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_validates_uniqueness(
        self, mock_password_hasher, mock_unit_of_work
    ):
        """Test that handler validates email and username uniqueness."""
        handler = CreateUserHandler(password_hasher=mock_password_hasher)
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        await handler.handle(command, mock_unit_of_work)

        # Verify read repository was used for validation
        mock_unit_of_work.users_read.get_by_email.assert_called_once()
        mock_unit_of_work.users_read.get_by_username.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_hashes_password(
        self, mock_password_hasher, mock_unit_of_work
    ):
        """Test that handler hashes password."""
        handler = CreateUserHandler(password_hasher=mock_password_hasher)
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        await handler.handle(command, mock_unit_of_work)

        mock_password_hasher.hash.assert_called_once_with("password123")

    @pytest.mark.asyncio
    async def test_create_user_collects_events(
        self, mock_password_hasher, mock_unit_of_work
    ):
        """Test that handler collects domain events via UoW."""
        handler = CreateUserHandler(password_hasher=mock_password_hasher)
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        await handler.handle(command, mock_unit_of_work)

        # Events are collected by UoW (not published directly)
        mock_unit_of_work.collect_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_error(
        self, mock_password_hasher, mock_unit_of_work
    ):
        """Test that duplicate email raises UserAlreadyExists."""
        # Setup: email already exists
        existing_user = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("existinguser"),
            password="hash",
        )
        mock_unit_of_work.users_read.get_by_email = AsyncMock(
            return_value=existing_user
        )

        handler = CreateUserHandler(password_hasher=mock_password_hasher)
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        with pytest.raises(UserAlreadyExists):
            await handler.handle(command, mock_unit_of_work)

        mock_unit_of_work.users.save.assert_not_called()


class TestUpdateUserHandler:
    """Tests for UpdateUserHandler.

    The handler now:
    - Takes only password_hasher in constructor
    - Receives UoW as parameter to handle() method
    - Uses uow.users for write operations
    - Uses uow.users_read for validation and fetching
    - Calls uow.collect_events() for event publishing
    """

    @pytest.fixture
    def existing_aggregate(self):
        """Create an existing user aggregate."""
        return UserAggregate.create(
            email=Email("existing@example.com"),
            username=Username("existinguser"),
            password="existing_hash",
            full_name="Existing User",
        )

    @pytest.fixture
    def handler(self, mock_password_hasher):
        """Create handler with mocked dependencies."""
        return UpdateUserHandler(password_hasher=mock_password_hasher)

    @pytest.mark.asyncio
    async def test_update_user_email(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test updating user email."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )

        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            email="new@example.com",
        )

        result = await handler.handle(command, mock_unit_of_work)

        assert result == existing_aggregate.id_str
        assert existing_aggregate.user.email_str == "new@example.com"

    @pytest.mark.asyncio
    async def test_update_user_username(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test updating user username."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )

        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            username="newusername",
        )

        result = await handler.handle(command, mock_unit_of_work)

        assert result == existing_aggregate.id_str
        assert existing_aggregate.user.username_str == "newusername"

    @pytest.mark.asyncio
    async def test_update_user_full_name(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test updating user full name."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )

        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            full_name="New Full Name",
        )

        result = await handler.handle(command, mock_unit_of_work)

        assert result == existing_aggregate.id_str
        assert existing_aggregate.user.full_name == "New Full Name"

    @pytest.mark.asyncio
    async def test_update_user_password(
        self, handler, existing_aggregate, mock_password_hasher, mock_unit_of_work
    ):
        """Test updating user password."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )
        mock_password_hasher.hash.return_value = "new_hashed_password"

        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            password="newpassword123",
        )

        result = await handler.handle(command, mock_unit_of_work)

        assert result == existing_aggregate.id_str
        mock_password_hasher.hash.assert_called_with("newpassword123")

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, mock_password_hasher, mock_unit_of_work):
        """Test that updating non-existent user raises UserNotFound."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(return_value=None)

        handler = UpdateUserHandler(password_hasher=mock_password_hasher)
        command = UpdateUserCommand(
            user_id="00000000-0000-0000-0000-000000000000",
            email="new@example.com",
        )

        with pytest.raises(UserNotFound):
            await handler.handle(command, mock_unit_of_work)

    @pytest.mark.asyncio
    async def test_update_user_collects_events(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test that handler collects domain events via UoW."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )
        existing_aggregate.clear_events()  # Clear creation event

        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            email="new@example.com",
        )

        await handler.handle(command, mock_unit_of_work)

        mock_unit_of_work.collect_events.assert_called_once()


class TestDeleteUserHandler:
    """Tests for DeleteUserHandler.

    The handler now:
    - Takes no dependencies in constructor
    - Receives UoW as parameter to handle() method
    - Uses uow.users for write operations
    - Uses uow.users_read for validation and fetching
    - Calls uow.collect_events() for event publishing
    """

    @pytest.fixture
    def existing_aggregate(self):
        """Create an existing user aggregate."""
        return UserAggregate.create(
            email=Email("existing@example.com"),
            username=Username("existinguser"),
            password="existing_hash",
        )

    @pytest.fixture
    def handler(self):
        """Create handler (no dependencies needed)."""
        return DeleteUserHandler()

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test successful user deletion."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )

        command = DeleteUserCommand(user_id=existing_aggregate.id_str)

        result = await handler.handle(command, mock_unit_of_work)

        assert result is True
        assert existing_aggregate.user.is_deleted is True

    @pytest.mark.asyncio
    async def test_delete_user_with_deleted_by(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test deletion with deleted_by parameter."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )
        deleter_id = "12345678-1234-5678-1234-567812345678"

        command = DeleteUserCommand(
            user_id=existing_aggregate.id_str,
            deleted_by=deleter_id,
        )

        result = await handler.handle(command, mock_unit_of_work)

        assert result is True
        assert existing_aggregate.user.deleted_by == UUID(deleter_id)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_unit_of_work):
        """Test that deleting non-existent user raises UserNotFound."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(return_value=None)

        handler = DeleteUserHandler()
        command = DeleteUserCommand(user_id="00000000-0000-0000-0000-000000000000")

        with pytest.raises(UserNotFound):
            await handler.handle(command, mock_unit_of_work)

    @pytest.mark.asyncio
    async def test_delete_user_collects_events(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test that handler collects domain events via UoW."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )
        existing_aggregate.clear_events()  # Clear creation event

        command = DeleteUserCommand(user_id=existing_aggregate.id_str)

        await handler.handle(command, mock_unit_of_work)

        mock_unit_of_work.collect_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_saves_aggregate(
        self, handler, existing_aggregate, mock_unit_of_work
    ):
        """Test that handler saves aggregate after deletion."""
        mock_unit_of_work.users_read.get_by_id = AsyncMock(
            return_value=existing_aggregate
        )

        command = DeleteUserCommand(user_id=existing_aggregate.id_str)

        await handler.handle(command, mock_unit_of_work)

        mock_unit_of_work.users.save.assert_called_once()
