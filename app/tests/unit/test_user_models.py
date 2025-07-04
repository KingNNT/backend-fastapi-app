import pytest
from datetime import datetime, timezone

from beanie import PydanticObjectId
from pydantic import ValidationError

from app.internal.dtos.user import UserCreate, UserUpdate, UserResponse


class TestUserDTOs:
    """Unit tests for User DTOs."""

    def test_user_create_valid(self):
        """Test valid UserCreate DTO."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123",
            "is_active": True,
        }

        user_create = UserCreate(**user_data)  # type: ignore

        assert user_create.email == "test@example.com"
        assert user_create.username == "testuser"
        assert user_create.full_name == "Test User"
        assert user_create.password == "password123"
        assert user_create.is_active is True

    def test_user_create_minimal(self):
        """Test UserCreate with minimal required fields."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        }

        user_create = UserCreate(**user_data)  # type: ignore

        assert user_create.email == "test@example.com"
        assert user_create.username == "testuser"
        assert user_create.password == "password123"
        assert user_create.full_name is None
        assert user_create.is_active is True  # default value

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)  # type: ignore

        assert "value is not a valid email address" in str(exc_info.value)

    def test_user_create_short_username(self):
        """Test UserCreate with username too short."""
        user_data = {
            "email": "test@example.com",
            "username": "ab",  # too short
            "password": "password123",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)  # type: ignore

        assert "at least 3 characters" in str(exc_info.value)

    def test_user_create_long_username(self):
        """Test UserCreate with username too long."""
        user_data = {
            "email": "test@example.com",
            "username": "a" * 51,  # too long
            "password": "password123",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)  # type: ignore

        assert "at most 50 characters" in str(exc_info.value)

    def test_user_create_short_password(self):
        """Test UserCreate with password too short."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "1234567",  # too short
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)  # type: ignore

        assert "at least 8 characters" in str(exc_info.value)

    def test_user_update_partial(self):
        """Test UserUpdate with partial data."""
        update_data = {"full_name": "Updated Name"}

        user_update = UserUpdate(**update_data)  # type: ignore

        assert user_update.full_name == "Updated Name"
        assert user_update.email is None
        assert user_update.username is None
        assert user_update.is_active is None

    def test_user_update_empty(self):
        """Test UserUpdate with no data."""
        user_update = UserUpdate()

        assert user_update.email is None
        assert user_update.username is None
        assert user_update.full_name is None
        assert user_update.is_active is None

    def test_user_update_invalid_email(self):
        """Test UserUpdate with invalid email."""
        update_data = {"email": "invalid-email"}

        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**update_data)  # type: ignore

        assert "value is not a valid email address" in str(exc_info.value)

    def test_user_response_valid(self):
        """Test valid UserResponse DTO."""
        user_id = PydanticObjectId()
        now = datetime.now(timezone.utc)

        response_data = {
            "id": user_id,
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        user_response = UserResponse(**response_data)

        assert user_response.id == user_id
        assert user_response.email == "test@example.com"
        assert user_response.username == "testuser"
        assert user_response.full_name == "Test User"
        assert user_response.is_active is True
        assert user_response.created_at == now
        assert user_response.updated_at == now


# Note: User model tests removed because they require MongoDB initialization
# These tests should be part of integration tests with a test database
