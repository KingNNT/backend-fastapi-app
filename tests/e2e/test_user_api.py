"""E2E tests for User API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.iam.application.read_models.user_read_model import UserReadModel
from app.iam.domain.user.exceptions import UserAlreadyExists, UserNotFound
from app.platform.web import register_exception_handlers
from app.presentation.api import api_router
from app.presentation.dependencies import (
    get_create_user_handler,
    get_delete_user_handler,
    get_list_users_handler,
    get_update_user_handler,
    get_user_by_email_handler,
    get_user_by_id_handler,
    get_user_by_username_handler,
)
from app.presentation.dependencies.repositories import get_unit_of_work


def create_mock_uow():
    """Create a mock Unit of Work for tests."""
    mock = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    mock.commit = AsyncMock(return_value=None)
    mock.rollback = AsyncMock(return_value=None)
    mock.collect_events = MagicMock(return_value=None)
    return mock


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    test_app = FastAPI()
    register_exception_handlers(test_app)
    test_app.include_router(api_router)
    return test_app


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


class TestCreateUserEndpoint:
    """Tests for POST /v1/users/."""

    def test_create_user_success(self, app):
        """Test successful user creation."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(
            return_value="12345678-1234-5678-1234-567812345678"
        )

        app.dependency_overrides[get_create_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.post(
            "/v1/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123",
                "full_name": "Test User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "12345678-1234-5678-1234-567812345678"

        app.dependency_overrides.clear()

    def test_create_user_duplicate_email(self, app):
        """Test creating user with duplicate email returns 409."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(
            side_effect=UserAlreadyExists("email", "test@example.com")
        )

        app.dependency_overrides[get_create_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.post(
            "/v1/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False

        app.dependency_overrides.clear()

    def test_create_user_validation_error(self, app):
        """Test creating user with invalid data returns 422."""
        mock_handler = AsyncMock()

        app.dependency_overrides[get_create_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.post(
            "/v1/users/",
            json={
                "email": "invalid-email",  # Invalid email format
                "username": "te",  # Too short
                "password": "short",  # Too short
            },
        )

        assert response.status_code == 422

        app.dependency_overrides.clear()


class TestGetUserEndpoint:
    """Tests for GET /v1/users/{user_id}."""

    def test_get_user_success(self, app, sample_user_read_model):
        """Test getting user by ID successfully."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=sample_user_read_model)

        app.dependency_overrides[get_user_by_id_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/12345678-1234-5678-1234-567812345678")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_user_read_model.id
        assert data["data"]["email"] == sample_user_read_model.email

        app.dependency_overrides.clear()

    def test_get_user_not_found(self, app):
        """Test getting non-existent user returns 404."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=None)

        app.dependency_overrides[get_user_by_id_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

        app.dependency_overrides.clear()


class TestGetUserByEmailEndpoint:
    """Tests for GET /v1/users/by-email/{email}."""

    def test_get_user_by_email_success(self, app, sample_user_read_model):
        """Test getting user by email successfully."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=sample_user_read_model)

        app.dependency_overrides[get_user_by_email_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/by-email/test@example.com")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == sample_user_read_model.email

        app.dependency_overrides.clear()

    def test_get_user_by_email_not_found(self, app):
        """Test getting user by non-existent email returns 404."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=None)

        app.dependency_overrides[get_user_by_email_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/by-email/notfound@example.com")

        assert response.status_code == 404

        app.dependency_overrides.clear()


class TestGetUserByUsernameEndpoint:
    """Tests for GET /v1/users/by-username/{username}."""

    def test_get_user_by_username_success(self, app, sample_user_read_model):
        """Test getting user by username successfully."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=sample_user_read_model)

        app.dependency_overrides[get_user_by_username_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/by-username/testuser")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == sample_user_read_model.username

        app.dependency_overrides.clear()

    def test_get_user_by_username_not_found(self, app):
        """Test getting user by non-existent username returns 404."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=None)

        app.dependency_overrides[get_user_by_username_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/by-username/notfound")

        assert response.status_code == 404

        app.dependency_overrides.clear()


class TestListUsersEndpoint:
    """Tests for GET /v1/users/."""

    def test_list_users_success(self, app, sample_user_list):
        """Test listing users successfully."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=sample_user_list)

        app.dependency_overrides[get_list_users_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 3
        assert len(data["data"]["data"]) == 3

        app.dependency_overrides.clear()

    def test_list_users_with_pagination(self, app, sample_user_list):
        """Test listing users with pagination parameters."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=sample_user_list[:1])

        app.dependency_overrides[get_list_users_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/?skip=10&limit=1")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["skip"] == 10
        assert data["data"]["limit"] == 1

        app.dependency_overrides.clear()

    def test_list_users_empty(self, app):
        """Test listing users when empty."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=[])

        app.dependency_overrides[get_list_users_handler] = lambda: mock_handler
        client = TestClient(app)

        response = client.get("/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 0
        assert data["data"]["data"] == []

        app.dependency_overrides.clear()


class TestUpdateUserEndpoint:
    """Tests for PUT /v1/users/{user_id}."""

    def test_update_user_success(self, app):
        """Test updating user successfully."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(
            return_value="12345678-1234-5678-1234-567812345678"
        )

        app.dependency_overrides[get_update_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.put(
            "/v1/users/12345678-1234-5678-1234-567812345678",
            json={
                "email": "newemail@example.com",
                "full_name": "New Name",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "12345678-1234-5678-1234-567812345678"

        app.dependency_overrides.clear()

    def test_update_user_not_found(self, app):
        """Test updating non-existent user returns 404."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(
            side_effect=UserNotFound("00000000-0000-0000-0000-000000000000")
        )

        app.dependency_overrides[get_update_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.put(
            "/v1/users/00000000-0000-0000-0000-000000000000",
            json={
                "email": "newemail@example.com",
            },
        )

        assert response.status_code == 404

        app.dependency_overrides.clear()

    def test_update_user_duplicate_email(self, app):
        """Test updating user with duplicate email returns 409."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(
            side_effect=UserAlreadyExists("email", "existing@example.com")
        )

        app.dependency_overrides[get_update_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.put(
            "/v1/users/12345678-1234-5678-1234-567812345678",
            json={
                "email": "existing@example.com",
            },
        )

        assert response.status_code == 409

        app.dependency_overrides.clear()


class TestDeleteUserEndpoint:
    """Tests for DELETE /v1/users/{user_id}."""

    def test_delete_user_success(self, app):
        """Test deleting user successfully."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(return_value=True)

        app.dependency_overrides[get_delete_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.delete("/v1/users/12345678-1234-5678-1234-567812345678")

        assert response.status_code == 204

        app.dependency_overrides.clear()

    def test_delete_user_not_found(self, app):
        """Test deleting non-existent user returns 404."""
        mock_handler = AsyncMock()
        mock_handler.handle = AsyncMock(
            side_effect=UserNotFound("00000000-0000-0000-0000-000000000000")
        )

        app.dependency_overrides[get_delete_user_handler] = lambda: mock_handler
        app.dependency_overrides[get_unit_of_work] = create_mock_uow
        client = TestClient(app)

        response = client.delete("/v1/users/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404

        app.dependency_overrides.clear()
