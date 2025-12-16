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
    """Tests for CreateUserHandler."""

    @pytest.fixture
    def handler(self, mock_user_repository, mock_event_bus, mock_password_hasher):
        """Create handler with mocked dependencies."""
        mock_domain_service = AsyncMock()
        mock_domain_service.validate_new_user = AsyncMock(return_value=None)

        return CreateUserHandler(
            repository=mock_user_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )

    @pytest.mark.asyncio
    async def test_create_user_success(self, handler, mock_user_repository):
        """Test successful user creation."""
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User",
        )

        user_id = await handler.handle(command)

        assert user_id is not None
        assert isinstance(user_id, str)
        mock_user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_validates_uniqueness(
        self, mock_user_repository, mock_event_bus, mock_password_hasher
    ):
        """Test that handler validates email and username uniqueness."""
        mock_domain_service = AsyncMock()
        mock_domain_service.validate_new_user = AsyncMock(return_value=None)

        handler = CreateUserHandler(
            repository=mock_user_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        await handler.handle(command)

        mock_domain_service.validate_new_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_hashes_password(
        self, mock_user_repository, mock_event_bus, mock_password_hasher
    ):
        """Test that handler hashes password."""
        mock_domain_service = AsyncMock()
        mock_domain_service.validate_new_user = AsyncMock(return_value=None)

        handler = CreateUserHandler(
            repository=mock_user_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        await handler.handle(command)

        mock_password_hasher.hash.assert_called_once_with("password123")

    @pytest.mark.asyncio
    async def test_create_user_publishes_events(
        self, mock_user_repository, mock_event_bus, mock_password_hasher
    ):
        """Test that handler publishes domain events."""
        mock_domain_service = AsyncMock()
        mock_domain_service.validate_new_user = AsyncMock(return_value=None)

        handler = CreateUserHandler(
            repository=mock_user_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        await handler.handle(command)

        mock_event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_error(
        self, mock_user_repository, mock_event_bus, mock_password_hasher
    ):
        """Test that duplicate email raises UserAlreadyExists."""
        mock_domain_service = AsyncMock()
        mock_domain_service.validate_new_user = AsyncMock(
            side_effect=UserAlreadyExists("email", "test@example.com")
        )

        handler = CreateUserHandler(
            repository=mock_user_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )
        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
        )

        with pytest.raises(UserAlreadyExists):
            await handler.handle(command)

        mock_user_repository.save.assert_not_called()


class TestUpdateUserHandler:
    """Tests for UpdateUserHandler."""

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
    def handler(
        self,
        mock_user_repository,
        mock_event_bus,
        mock_password_hasher,
        existing_aggregate,
    ):
        """Create handler with mocked dependencies."""
        mock_domain_service = AsyncMock()
        mock_domain_service.ensure_email_unique = AsyncMock(return_value=None)
        mock_domain_service.ensure_username_unique = AsyncMock(return_value=None)
        mock_user_repository.get_by_id = AsyncMock(return_value=existing_aggregate)

        return UpdateUserHandler(
            repository=mock_user_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )

    @pytest.mark.asyncio
    async def test_update_user_email(self, handler, existing_aggregate):
        """Test updating user email."""
        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            email="new@example.com",
        )

        result = await handler.handle(command)

        assert result == existing_aggregate.id_str
        assert existing_aggregate.user.email_str == "new@example.com"

    @pytest.mark.asyncio
    async def test_update_user_username(self, handler, existing_aggregate):
        """Test updating user username."""
        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            username="newusername",
        )

        result = await handler.handle(command)

        assert result == existing_aggregate.id_str
        assert existing_aggregate.user.username_str == "newusername"

    @pytest.mark.asyncio
    async def test_update_user_full_name(self, handler, existing_aggregate):
        """Test updating user full name."""
        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            full_name="New Full Name",
        )

        result = await handler.handle(command)

        assert result == existing_aggregate.id_str
        assert existing_aggregate.user.full_name == "New Full Name"

    @pytest.mark.asyncio
    async def test_update_user_password(
        self, handler, existing_aggregate, mock_password_hasher
    ):
        """Test updating user password."""
        mock_password_hasher.hash.return_value = "new_hashed_password"
        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            password="newpassword123",
        )

        result = await handler.handle(command)

        assert result == existing_aggregate.id_str
        mock_password_hasher.hash.assert_called_with("newpassword123")

    @pytest.mark.asyncio
    async def test_update_user_not_found(
        self, mock_user_repository, mock_event_bus, mock_password_hasher
    ):
        """Test that updating non-existent user raises UserNotFound."""
        mock_domain_service = AsyncMock()
        mock_user_repository.get_by_id = AsyncMock(return_value=None)

        handler = UpdateUserHandler(
            repository=mock_user_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )
        command = UpdateUserCommand(
            user_id="00000000-0000-0000-0000-000000000000",
            email="new@example.com",
        )

        with pytest.raises(UserNotFound):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_update_user_publishes_events(
        self, handler, existing_aggregate, mock_event_bus
    ):
        """Test that handler publishes domain events."""
        existing_aggregate.clear_events()  # Clear creation event
        command = UpdateUserCommand(
            user_id=existing_aggregate.id_str,
            email="new@example.com",
        )

        await handler.handle(command)

        mock_event_bus.publish.assert_called()


class TestDeleteUserHandler:
    """Tests for DeleteUserHandler."""

    @pytest.fixture
    def existing_aggregate(self):
        """Create an existing user aggregate."""
        return UserAggregate.create(
            email=Email("existing@example.com"),
            username=Username("existinguser"),
            password="existing_hash",
        )

    @pytest.fixture
    def handler(self, mock_user_repository, mock_event_bus, existing_aggregate):
        """Create handler with mocked dependencies."""
        mock_user_repository.get_by_id = AsyncMock(return_value=existing_aggregate)

        return DeleteUserHandler(
            repository=mock_user_repository,
            event_bus=mock_event_bus,
        )

    @pytest.mark.asyncio
    async def test_delete_user_success(self, handler, existing_aggregate):
        """Test successful user deletion."""
        command = DeleteUserCommand(user_id=existing_aggregate.id_str)

        result = await handler.handle(command)

        assert result is True
        assert existing_aggregate.user.is_deleted is True

    @pytest.mark.asyncio
    async def test_delete_user_with_deleted_by(self, handler, existing_aggregate):
        """Test deletion with deleted_by parameter."""
        deleter_id = "12345678-1234-5678-1234-567812345678"
        command = DeleteUserCommand(
            user_id=existing_aggregate.id_str,
            deleted_by=deleter_id,
        )

        result = await handler.handle(command)

        assert result is True
        assert existing_aggregate.user.deleted_by == UUID(deleter_id)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_user_repository, mock_event_bus):
        """Test that deleting non-existent user raises UserNotFound."""
        mock_user_repository.get_by_id = AsyncMock(return_value=None)

        handler = DeleteUserHandler(
            repository=mock_user_repository,
            event_bus=mock_event_bus,
        )
        command = DeleteUserCommand(user_id="00000000-0000-0000-0000-000000000000")

        with pytest.raises(UserNotFound):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_user_publishes_events(
        self, handler, existing_aggregate, mock_event_bus
    ):
        """Test that handler publishes domain events."""
        existing_aggregate.clear_events()  # Clear creation event
        command = DeleteUserCommand(user_id=existing_aggregate.id_str)

        await handler.handle(command)

        mock_event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_delete_user_saves_aggregate(
        self, handler, existing_aggregate, mock_user_repository
    ):
        """Test that handler saves aggregate after deletion."""
        command = DeleteUserCommand(user_id=existing_aggregate.id_str)

        await handler.handle(command)

        mock_user_repository.save.assert_called_once()
