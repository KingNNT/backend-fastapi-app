"""Integration tests for PostgreSQL user repository."""

from uuid import UUID

import pytest

from app.core.domain.aggregates import UserAggregate
from app.core.domain.value_objects import Email, Username
from app.infrastructure.persistence.postgresql.repositories.user_read import (
    PostgresUserReadModelRepository,
    PostgresUserReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.user_write import (
    PostgresUserWriteRepository,
)

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestPostgresUserWriteRepository:
    """Integration tests for PostgresUserWriteRepository."""

    async def test_save_and_retrieve_user(self, postgres_session):
        """Test creating a user and retrieving it by ID."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        # Create user aggregate
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hashed_password_123",
            full_name="Test User",
        )

        # Save user
        await write_repo.save(aggregate)

        # Retrieve user
        retrieved = await read_repo.get_by_id(aggregate.id)

        assert retrieved is not None
        assert retrieved.user.email_str == "test@example.com"
        assert retrieved.user.username_str == "testuser"
        assert retrieved.user.full_name == "Test User"
        assert retrieved.user.password == "hashed_password_123"
        assert retrieved.user.is_active is True

    async def test_save_updates_existing_user(self, postgres_session):
        """Test updating an existing user."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        # Create and save user
        aggregate = UserAggregate.create(
            email=Email("original@example.com"),
            username=Username("originaluser"),
            password="original_hash",
            full_name="Original Name",
        )
        await write_repo.save(aggregate)

        # Update user
        aggregate.update_email(Email("updated@example.com"))
        aggregate.update_profile(full_name="Updated Name")
        await write_repo.save(aggregate)

        # Retrieve and verify
        retrieved = await read_repo.get_by_id(aggregate.id)

        assert retrieved is not None
        assert retrieved.user.email_str == "updated@example.com"
        assert retrieved.user.full_name == "Updated Name"
        assert retrieved.user.username_str == "originaluser"

    async def test_soft_delete_user(self, postgres_session):
        """Test soft deleting a user excludes it from queries."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        # Create and save user
        aggregate = UserAggregate.create(
            email=Email("delete@example.com"),
            username=Username("deleteuser"),
            password="hash",
        )
        await write_repo.save(aggregate)

        # Verify user exists
        retrieved = await read_repo.get_by_id(aggregate.id)
        assert retrieved is not None

        # Soft delete
        deleter_id = UUID("12345678-1234-5678-1234-567812345678")
        aggregate.soft_delete(deleted_by=deleter_id)
        await write_repo.save(aggregate)

        # User should not be found (excluded by default)
        retrieved = await read_repo.get_by_id(aggregate.id)
        assert retrieved is None

    async def test_exists_by_email(self, postgres_session):
        """Test checking if email exists."""
        write_repo = PostgresUserWriteRepository(postgres_session)

        email = Email("exists@example.com")

        # Should not exist initially
        assert await write_repo.exists_by_email(email) is False

        # Create user with email
        aggregate = UserAggregate.create(
            email=email,
            username=Username("existsuser"),
            password="hash",
        )
        await write_repo.save(aggregate)

        # Should exist now
        assert await write_repo.exists_by_email(email) is True

        # Different email should not exist
        assert await write_repo.exists_by_email(Email("other@example.com")) is False

    async def test_exists_by_username(self, postgres_session):
        """Test checking if username exists."""
        write_repo = PostgresUserWriteRepository(postgres_session)

        username = Username("uniqueuser")

        # Should not exist initially
        assert await write_repo.exists_by_username(username) is False

        # Create user with username
        aggregate = UserAggregate.create(
            email=Email("unique@example.com"),
            username=username,
            password="hash",
        )
        await write_repo.save(aggregate)

        # Should exist now
        assert await write_repo.exists_by_username(username) is True

        # Different username should not exist
        assert await write_repo.exists_by_username(Username("otheruser")) is False


class TestPostgresUserReadRepository:
    """Integration tests for PostgresUserReadRepository."""

    async def test_get_by_email(self, postgres_session):
        """Test retrieving user by email."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        email = Email("byemail@example.com")
        aggregate = UserAggregate.create(
            email=email,
            username=Username("byemailuser"),
            password="hash",
        )
        await write_repo.save(aggregate)

        # Retrieve by email
        retrieved = await read_repo.get_by_email(email)

        assert retrieved is not None
        assert retrieved.user.email == email
        assert retrieved.id == aggregate.id

    async def test_get_by_username(self, postgres_session):
        """Test retrieving user by username."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        username = Username("byusername")
        aggregate = UserAggregate.create(
            email=Email("byusername@example.com"),
            username=username,
            password="hash",
        )
        await write_repo.save(aggregate)

        # Retrieve by username
        retrieved = await read_repo.get_by_username(username)

        assert retrieved is not None
        assert retrieved.user.username == username
        assert retrieved.id == aggregate.id

    async def test_list_users_pagination(self, postgres_session):
        """Test listing users with pagination."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        # Create multiple users
        for i in range(5):
            aggregate = UserAggregate.create(
                email=Email(f"user{i}@example.com"),
                username=Username(f"listuser{i}"),
                password="hash",
            )
            await write_repo.save(aggregate)

        # Test pagination
        page1 = await read_repo.list_all(skip=0, limit=2)
        page2 = await read_repo.list_all(skip=2, limit=2)
        page3 = await read_repo.list_all(skip=4, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_list_users_include_deleted(self, postgres_session):
        """Test listing users with include_deleted flag."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        # Create active user
        active = UserAggregate.create(
            email=Email("active@example.com"),
            username=Username("activeuser"),
            password="hash",
        )
        await write_repo.save(active)

        # Create and delete user
        deleted = UserAggregate.create(
            email=Email("deleted@example.com"),
            username=Username("deleteduser"),
            password="hash",
        )
        await write_repo.save(deleted)
        deleted.soft_delete()
        await write_repo.save(deleted)

        # Without include_deleted
        users = await read_repo.list_all(include_deleted=False)
        assert len(users) == 1
        assert users[0].user.email_str == "active@example.com"

        # With include_deleted
        users = await read_repo.list_all(include_deleted=True)
        assert len(users) == 2

    async def test_count_users(self, postgres_session):
        """Test counting users."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_repo = PostgresUserReadRepository(postgres_session)

        # Initially zero
        assert await read_repo.count() == 0

        # Create users
        for i in range(3):
            aggregate = UserAggregate.create(
                email=Email(f"count{i}@example.com"),
                username=Username(f"countuser{i}"),
                password="hash",
            )
            await write_repo.save(aggregate)

        # Count should be 3
        assert await read_repo.count() == 3

        # Delete one user
        users = await read_repo.list_all()
        users[0].soft_delete()
        await write_repo.save(users[0])

        # Count without deleted
        assert await read_repo.count(include_deleted=False) == 2

        # Count with deleted
        assert await read_repo.count(include_deleted=True) == 3


class TestPostgresUserReadModelRepository:
    """Integration tests for PostgresUserReadModelRepository."""

    async def test_get_by_id_returns_read_model(self, postgres_session):
        """Test getting user returns UserReadModel."""
        write_repo = PostgresUserWriteRepository(postgres_session)
        read_model_repo = PostgresUserReadModelRepository(postgres_session)

        aggregate = UserAggregate.create(
            email=Email("readmodel@example.com"),
            username=Username("readmodeluser"),
            password="hash",
            full_name="Read Model User",
        )
        await write_repo.save(aggregate)

        # Get read model
        read_model = await read_model_repo.get_by_id(aggregate.id_str)

        assert read_model is not None
        assert read_model.id == aggregate.id_str
        assert read_model.email == "readmodel@example.com"
        assert read_model.username == "readmodeluser"
        assert read_model.full_name == "Read Model User"
        assert read_model.is_active is True
        assert read_model.created_at is not None
        assert read_model.updated_at is not None
        assert read_model.deleted_at is None

    async def test_get_by_invalid_id_returns_none(self, postgres_session):
        """Test getting user with invalid ID returns None."""
        read_model_repo = PostgresUserReadModelRepository(postgres_session)

        result = await read_model_repo.get_by_id("invalid-uuid")
        assert result is None

        result = await read_model_repo.get_by_id("00000000-0000-0000-0000-000000000000")
        assert result is None
