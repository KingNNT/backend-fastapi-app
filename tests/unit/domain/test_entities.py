"""Unit tests for domain entities."""

import time
from uuid import UUID

from app.core.domain.entities import User
from app.core.domain.value_objects import Email, Username
from app.shared.domain.base_entity import BaseEntity, utc_now
from app.shared.domain.ids import UserId


class TestBaseEntity:
    """Tests for BaseEntity."""

    def test_base_entity_created_at_default(self):
        """Test that created_at is set to current UTC time by default."""
        before = utc_now()
        entity = BaseEntity()
        after = utc_now()
        assert before <= entity.created_at <= after

    def test_base_entity_updated_at_default(self):
        """Test that updated_at is set to current UTC time by default."""
        before = utc_now()
        entity = BaseEntity()
        after = utc_now()
        assert before <= entity.updated_at <= after

    def test_base_entity_is_deleted_false_by_default(self):
        """Test that entity is not deleted by default."""
        entity = BaseEntity()
        assert entity.is_deleted is False
        assert entity.deleted_at is None
        assert entity.deleted_by is None

    def test_soft_delete(self):
        """Test soft deletion marks entity as deleted."""
        entity = BaseEntity()
        deleter_id = UUID("12345678-1234-5678-1234-567812345678")

        entity.soft_delete(deleted_by=deleter_id)

        assert entity.is_deleted is True
        assert entity.deleted_at is not None
        assert entity.deleted_by == deleter_id

    def test_soft_delete_without_deleted_by(self):
        """Test soft deletion without specifying who deleted."""
        entity = BaseEntity()

        entity.soft_delete()

        assert entity.is_deleted is True
        assert entity.deleted_at is not None
        assert entity.deleted_by is None

    def test_mark_updated(self):
        """Test marking entity as updated."""
        entity = BaseEntity()
        original_updated_at = entity.updated_at
        updater_id = UUID("12345678-1234-5678-1234-567812345678")

        # Small delay to ensure time difference
        time.sleep(0.001)

        entity.mark_updated(updated_by=updater_id)

        assert entity.updated_at > original_updated_at
        assert entity.updated_by == updater_id


class TestUserEntity:
    """Tests for User entity."""

    def test_create_user_with_value_objects(self):
        """Test creating user with value objects."""
        user_id = UserId.generate()
        email = Email("test@example.com")
        username = Username("testuser")

        user = User(
            id=user_id,
            email=email,
            username=username,
            password="hashed_password",
            full_name="Test User",
        )

        assert user.id == user_id
        assert user.email == email
        assert user.username == username
        assert user.password == "hashed_password"
        assert user.full_name == "Test User"
        assert user.is_active is True

    def test_create_user_with_string_conversion(self):
        """Test that string values are converted to value objects."""
        user = User(
            email="test@example.com",  # type: ignore
            username="testuser",  # type: ignore
        )

        assert isinstance(user.email, Email)
        assert isinstance(user.username, Username)
        assert user.email.value == "test@example.com"
        assert user.username.value == "testuser"

    def test_user_deactivate(self):
        """Test deactivating a user."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        assert user.is_active is True

        user.deactivate()

        assert user.is_active is False

    def test_user_activate(self):
        """Test activating a user."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
            is_active=False,
        )

        user.activate()

        assert user.is_active is True

    def test_user_update_email(self):
        """Test updating user email."""
        user = User(
            email=Email("old@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        new_email = Email("new@example.com")

        user.update_email(new_email)

        assert user.email == new_email
        assert user.email_str == "new@example.com"

    def test_user_update_password(self):
        """Test updating user password."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="old_hash",
        )

        user.update_password("new_hash")

        assert user.password == "new_hash"

    def test_user_update_profile(self):
        """Test updating user profile."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
            full_name="Old Name",
        )
        new_username = Username("newuser")

        user.update_profile(full_name="New Name", username=new_username)

        assert user.full_name == "New Name"
        assert user.username == new_username

    def test_user_update_profile_partial(self):
        """Test updating only part of user profile."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
            full_name="Old Name",
        )

        user.update_profile(full_name="New Name")

        assert user.full_name == "New Name"
        assert user.username_str == "testuser"  # Unchanged

    def test_user_email_str_property(self):
        """Test email_str property returns string."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        assert user.email_str == "test@example.com"
        assert isinstance(user.email_str, str)

    def test_user_username_str_property(self):
        """Test username_str property returns string."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        assert user.username_str == "testuser"
        assert isinstance(user.username_str, str)

    def test_user_id_str_property(self):
        """Test id_str property returns string."""
        user_id = UserId.generate()
        user = User(
            id=user_id,
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        assert user.id_str == str(user_id)
        assert isinstance(user.id_str, str)

    def test_user_inherits_base_entity(self):
        """Test that User inherits from BaseEntity."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        assert isinstance(user, BaseEntity)
        assert hasattr(user, "created_at")
        assert hasattr(user, "updated_at")
        assert hasattr(user, "is_deleted")

    def test_user_soft_delete(self):
        """Test soft deleting a user."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        deleter_id = UUID("12345678-1234-5678-1234-567812345678")

        user.soft_delete(deleted_by=deleter_id)

        assert user.is_deleted is True
        assert user.deleted_by == deleter_id

    def test_user_default_full_name_is_none(self):
        """Test that full_name defaults to None."""
        user = User(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        assert user.full_name is None
