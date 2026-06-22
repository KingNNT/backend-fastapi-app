"""Unit tests for query handlers."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.iam.application.handlers import (
    GetUserByEmailHandler,
    GetUserByIdHandler,
    GetUserByUsernameHandler,
    ListUsersHandler,
)
from app.iam.application.queries.user import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    ListUsersQuery,
)
from app.iam.application.read_models.user_read_model import UserReadModel


@pytest.fixture
def sample_user_read_model():
    """Create a sample user read model."""
    now = datetime.now(timezone.utc)
    return UserReadModel(
        id="12345678-1234-5678-1234-567812345678",
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        is_active=True,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


@pytest.fixture
def sample_user_list():
    """Create a list of sample user read models."""
    now = datetime.now(timezone.utc)
    return [
        UserReadModel(
            id=f"user-id-{i}",
            email=f"user{i}@example.com",
            username=f"user{i}",
            full_name=f"User {i}",
            is_active=True,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        for i in range(3)
    ]


class TestGetUserByIdHandler:
    """Tests for GetUserByIdHandler."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(
        self, mock_user_read_model_repository, sample_user_read_model
    ):
        """Test getting user by ID when found."""
        mock_user_read_model_repository.get_by_id = AsyncMock(
            return_value=sample_user_read_model
        )
        handler = GetUserByIdHandler(repository=mock_user_read_model_repository)
        query = GetUserByIdQuery(user_id="12345678-1234-5678-1234-567812345678")

        result = await handler.handle(query)

        assert result is not None
        assert result.id == sample_user_read_model.id
        assert result.email == sample_user_read_model.email
        mock_user_read_model_repository.get_by_id.assert_called_once_with(query.user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_user_read_model_repository):
        """Test getting user by ID when not found."""
        mock_user_read_model_repository.get_by_id = AsyncMock(return_value=None)
        handler = GetUserByIdHandler(repository=mock_user_read_model_repository)
        query = GetUserByIdQuery(user_id="non-existent-id")

        result = await handler.handle(query)

        assert result is None
        mock_user_read_model_repository.get_by_id.assert_called_once_with(query.user_id)


class TestGetUserByEmailHandler:
    """Tests for GetUserByEmailHandler."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(
        self, mock_user_read_model_repository, sample_user_read_model
    ):
        """Test getting user by email when found."""
        mock_user_read_model_repository.get_by_email = AsyncMock(
            return_value=sample_user_read_model
        )
        handler = GetUserByEmailHandler(repository=mock_user_read_model_repository)
        query = GetUserByEmailQuery(email="test@example.com")

        result = await handler.handle(query)

        assert result is not None
        assert result.email == "test@example.com"
        mock_user_read_model_repository.get_by_email.assert_called_once_with(
            query.email
        )

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, mock_user_read_model_repository):
        """Test getting user by email when not found."""
        mock_user_read_model_repository.get_by_email = AsyncMock(return_value=None)
        handler = GetUserByEmailHandler(repository=mock_user_read_model_repository)
        query = GetUserByEmailQuery(email="notfound@example.com")

        result = await handler.handle(query)

        assert result is None
        mock_user_read_model_repository.get_by_email.assert_called_once_with(
            query.email
        )


class TestGetUserByUsernameHandler:
    """Tests for GetUserByUsernameHandler."""

    @pytest.mark.asyncio
    async def test_get_user_by_username_found(
        self, mock_user_read_model_repository, sample_user_read_model
    ):
        """Test getting user by username when found."""
        mock_user_read_model_repository.get_by_username = AsyncMock(
            return_value=sample_user_read_model
        )
        handler = GetUserByUsernameHandler(repository=mock_user_read_model_repository)
        query = GetUserByUsernameQuery(username="testuser")

        result = await handler.handle(query)

        assert result is not None
        assert result.username == "testuser"
        mock_user_read_model_repository.get_by_username.assert_called_once_with(
            query.username
        )

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(
        self, mock_user_read_model_repository
    ):
        """Test getting user by username when not found."""
        mock_user_read_model_repository.get_by_username = AsyncMock(return_value=None)
        handler = GetUserByUsernameHandler(repository=mock_user_read_model_repository)
        query = GetUserByUsernameQuery(username="notfound")

        result = await handler.handle(query)

        assert result is None
        mock_user_read_model_repository.get_by_username.assert_called_once_with(
            query.username
        )


class TestListUsersHandler:
    """Tests for ListUsersHandler."""

    @pytest.mark.asyncio
    async def test_list_users_default_pagination(
        self, mock_user_read_model_repository, sample_user_list
    ):
        """Test listing users with default pagination."""
        mock_user_read_model_repository.list_all = AsyncMock(
            return_value=sample_user_list
        )
        handler = ListUsersHandler(repository=mock_user_read_model_repository)
        query = ListUsersQuery()

        result = await handler.handle(query)

        assert len(result) == 3
        mock_user_read_model_repository.list_all.assert_called_once_with(
            skip=0,
            limit=100,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_users_custom_pagination(
        self, mock_user_read_model_repository, sample_user_list
    ):
        """Test listing users with custom pagination."""
        mock_user_read_model_repository.list_all = AsyncMock(
            return_value=sample_user_list[:1]
        )
        handler = ListUsersHandler(repository=mock_user_read_model_repository)
        query = ListUsersQuery(skip=10, limit=1)

        result = await handler.handle(query)

        assert len(result) == 1
        mock_user_read_model_repository.list_all.assert_called_once_with(
            skip=10,
            limit=1,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_users_include_deleted(
        self, mock_user_read_model_repository, sample_user_list
    ):
        """Test listing users including deleted ones."""
        mock_user_read_model_repository.list_all = AsyncMock(
            return_value=sample_user_list
        )
        handler = ListUsersHandler(repository=mock_user_read_model_repository)
        query = ListUsersQuery(include_deleted=True)

        await handler.handle(query)

        mock_user_read_model_repository.list_all.assert_called_once_with(
            skip=0,
            limit=100,
            include_deleted=True,
        )

    @pytest.mark.asyncio
    async def test_list_users_empty_result(self, mock_user_read_model_repository):
        """Test listing users when no users exist."""
        mock_user_read_model_repository.list_all = AsyncMock(return_value=[])
        handler = ListUsersHandler(repository=mock_user_read_model_repository)
        query = ListUsersQuery()

        result = await handler.handle(query)

        assert result == []
        assert len(result) == 0
