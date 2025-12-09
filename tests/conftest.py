"""Shared test fixtures and configuration."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.application.read_models import UserReadModel
from app.core.domain.aggregates import UserAggregate
from app.core.domain.entities import User
from app.core.domain.value_objects import Email, UserId, Username

# ============================================================================
# Value Object Fixtures
# ============================================================================


@pytest.fixture
def valid_email() -> Email:
    """Create a valid Email value object."""
    return Email("test@example.com")


@pytest.fixture
def valid_username() -> Username:
    """Create a valid Username value object."""
    return Username("testuser")


@pytest.fixture
def valid_user_id() -> UserId:
    """Create a valid UserId value object."""
    return UserId.generate()


# ============================================================================
# Entity Fixtures
# ============================================================================


@pytest.fixture
def user_entity(valid_user_id, valid_email, valid_username) -> User:
    """Create a User entity."""
    return User(
        id=valid_user_id,
        email=valid_email,
        username=valid_username,
        password_hash="hashed_password_123",
        full_name="Test User",
        is_active=True,
    )


# ============================================================================
# Aggregate Fixtures
# ============================================================================


@pytest.fixture
def user_aggregate(user_entity) -> UserAggregate:
    """Create a UserAggregate from an existing entity."""
    return UserAggregate.reconstitute(user_entity)


@pytest.fixture
def new_user_aggregate() -> UserAggregate:
    """Create a new UserAggregate (simulating creation)."""
    return UserAggregate.create(
        email=Email("newuser@example.com"),
        username=Username("newuser"),
        password_hash="hashed_password_456",
        full_name="New User",
    )


# ============================================================================
# Read Model Fixtures
# ============================================================================


@pytest.fixture
def user_read_model() -> UserReadModel:
    """Create a UserReadModel for query tests."""
    now = datetime.now(timezone.utc)
    return UserReadModel(
        id=str(uuid4()),
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        is_active=True,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


# ============================================================================
# Mock Repository Fixtures
# ============================================================================


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Create a mock user repository."""
    mock = AsyncMock()
    mock.save = AsyncMock(return_value=None)
    mock.delete = AsyncMock(return_value=None)
    mock.get_by_id = AsyncMock(return_value=None)
    mock.get_by_email = AsyncMock(return_value=None)
    mock.get_by_username = AsyncMock(return_value=None)
    mock.exists_by_email = AsyncMock(return_value=False)
    mock.exists_by_username = AsyncMock(return_value=False)
    mock.list_all = AsyncMock(return_value=[])
    mock.count = AsyncMock(return_value=0)
    return mock


@pytest.fixture
def mock_user_read_model_repository() -> AsyncMock:
    """Create a mock user read model repository."""
    mock = AsyncMock()
    mock.get_by_id = AsyncMock(return_value=None)
    mock.get_by_email = AsyncMock(return_value=None)
    mock.get_by_username = AsyncMock(return_value=None)
    mock.list_all = AsyncMock(return_value=[])
    mock.count = AsyncMock(return_value=0)
    return mock


# ============================================================================
# Mock Event Bus Fixture
# ============================================================================


@pytest.fixture
def mock_event_bus() -> AsyncMock:
    """Create a mock event bus."""
    mock = AsyncMock()
    mock.publish = AsyncMock(return_value=None)
    mock.subscribe = MagicMock(return_value=None)
    return mock


# ============================================================================
# Mock Password Hasher Fixture
# ============================================================================


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    """Create a mock password hasher."""
    mock = MagicMock()
    mock.hash = MagicMock(return_value="hashed_password")
    mock.verify = MagicMock(return_value=True)
    return mock
