import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from beanie import PydanticObjectId

from app.internal.dtos import UserCreate, UserUpdate, UserResponse
from app.internal.services import UserService
from app.internal.exceptions import UserAlreadyExists, UserNotFound


class MockUser:
    """Mock User model for testing without database."""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", PydanticObjectId())
        self.email = kwargs.get("email", "")
        self.username = kwargs.get("username", "")
        self.full_name = kwargs.get("full_name")
        self.is_active = kwargs.get("is_active", True)
        self.password_hash = kwargs.get("password_hash", "")
        self.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
        self.updated_at = kwargs.get("updated_at", datetime.now(timezone.utc))
        self.created_by = kwargs.get("created_by")
        self.updated_by = kwargs.get("updated_by")
        self.deleted_at = kwargs.get("deleted_at")
        self.deleted_by = kwargs.get("deleted_by")

    def model_dump(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "deleted_at": self.deleted_at,
            "deleted_by": self.deleted_by,
        }

    def soft_delete(self, deleted_by=None):
        now = datetime.now(timezone.utc)
        self.deleted_at = now
        self.deleted_by = deleted_by
        self.updated_at = now
        self.updated_by = deleted_by


class TestUserServiceBusiness:
    """Unit tests for UserService business logic."""

    @pytest.fixture
    def user_service(self):
        """Create a UserService instance with mocked repository."""
        service = UserService()
        service.repository = AsyncMock()
        return service

    @pytest.fixture
    def sample_user_create(self):
        """Sample UserCreate data."""
        return UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
            is_active=True,
        )

    @pytest.fixture
    def mock_user(self):
        """Mock User model."""
        return MockUser(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password_hash="hashed_password123",
            is_active=True,
        )

    @patch("app.internal.services.user.User")
    async def test_create_user_success(
        self, mock_user_class, user_service, sample_user_create, mock_user
    ):
        """Test successful user creation."""
        # Arrange
        user_service.repository.email_exists.return_value = False
        user_service.repository.username_exists.return_value = False
        user_service.repository.create.return_value = mock_user
        mock_user_class.return_value = mock_user

        # Act
        result = await user_service.create_user(sample_user_create)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.email == sample_user_create.email
        assert result.username == sample_user_create.username
        assert result.full_name == sample_user_create.full_name
        assert result.is_active == sample_user_create.is_active

        user_service.repository.email_exists.assert_called_once_with(
            sample_user_create.email
        )
        user_service.repository.username_exists.assert_called_once_with(
            sample_user_create.username
        )
        user_service.repository.create.assert_called_once()

    async def test_create_user_email_exists(self, user_service, sample_user_create):
        """Test user creation fails when email already exists."""
        # Arrange
        user_service.repository.email_exists.return_value = True

        # Act & Assert
        with pytest.raises(UserAlreadyExists) as exc_info:
            await user_service.create_user(sample_user_create)

        assert "email" in exc_info.value.message
        assert sample_user_create.email in exc_info.value.message

        user_service.repository.email_exists.assert_called_once_with(
            sample_user_create.email
        )
        user_service.repository.create.assert_not_called()

    async def test_create_user_username_exists(self, user_service, sample_user_create):
        """Test user creation fails when username already exists."""
        # Arrange
        user_service.repository.email_exists.return_value = False
        user_service.repository.username_exists.return_value = True

        # Act & Assert
        with pytest.raises(UserAlreadyExists) as exc_info:
            await user_service.create_user(sample_user_create)

        assert "username" in exc_info.value.message
        assert sample_user_create.username in exc_info.value.message

        user_service.repository.username_exists.assert_called_once_with(
            sample_user_create.username
        )
        user_service.repository.create.assert_not_called()

    async def test_get_user_success(self, user_service, mock_user):
        """Test successful user retrieval."""
        # Arrange
        user_id = mock_user.id
        user_service.repository.get_by_id.return_value = mock_user

        # Act
        result = await user_service.get_user(user_id)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.id == user_id
        assert result.email == mock_user.email

        user_service.repository.get_by_id.assert_called_once_with(user_id)

    async def test_get_user_not_found(self, user_service):
        """Test user retrieval when user doesn't exist."""
        # Arrange
        user_id = PydanticObjectId()
        user_service.repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFound) as exc_info:
            await user_service.get_user(user_id)

        assert str(user_id) in exc_info.value.message

    async def test_get_users_success(self, user_service, mock_user):
        """Test successful users list retrieval."""
        # Arrange
        users = [mock_user]
        user_service.repository.get_all.return_value = users

        # Act
        result = await user_service.get_users(skip=0, limit=100)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], UserResponse)
        assert result[0].id == mock_user.id

        user_service.repository.get_all.assert_called_once_with(
            skip=0, limit=100, email=None, username=None
        )

    async def test_update_user_success(self, user_service, mock_user):
        """Test successful user update."""
        # Arrange
        user_id = mock_user.id
        update_data = UserUpdate(full_name="Updated Name")  # type: ignore

        user_service.repository.get_by_id.return_value = mock_user
        user_service.repository.email_exists.return_value = False
        user_service.repository.username_exists.return_value = False
        user_service.repository.update.return_value = mock_user

        # Act
        result = await user_service.update_user(user_id, update_data)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.id == user_id

        user_service.repository.get_by_id.assert_called_once_with(user_id)
        user_service.repository.update.assert_called_once()

    async def test_update_user_not_found(self, user_service):
        """Test user update when user doesn't exist."""
        # Arrange
        user_id = PydanticObjectId()
        update_data = UserUpdate(full_name="Updated Name")  # type: ignore
        user_service.repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFound) as exc_info:
            await user_service.update_user(user_id, update_data)

        assert str(user_id) in exc_info.value.message

    async def test_delete_user_success(self, user_service, mock_user):
        """Test successful user deletion (soft delete)."""
        # Arrange
        user_id = mock_user.id
        user_service.repository.get_by_id.return_value = mock_user
        user_service.repository.delete.return_value = mock_user

        # Act
        result = await user_service.delete_user(user_id)

        # Assert
        assert result is True

        user_service.repository.get_by_id.assert_called_once_with(user_id)
        user_service.repository.delete.assert_called_once()

    async def test_delete_user_not_found(self, user_service):
        """Test user deletion when user doesn't exist."""
        # Arrange
        user_id = PydanticObjectId()
        user_service.repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFound) as exc_info:
            await user_service.delete_user(user_id)

        assert str(user_id) in exc_info.value.message
