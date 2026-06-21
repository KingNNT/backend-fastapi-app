"""Unit tests for domain aggregates."""

from uuid import UUID

import pytest

from app.iam.domain.user.aggregate import UserAggregate
from app.iam.domain.user.entity import User
from app.iam.domain.user.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserEmailUpdated,
    UserPasswordUpdated,
    UserUpdated,
)
from app.iam.domain.user.exceptions import InvalidUserState
from app.iam.domain.user.value_objects import Email, Username
from app.shared.domain.ids import UserId


class TestUserAggregate:
    """Tests for UserAggregate."""

    def test_create_aggregate(self):
        """Test creating a new user aggregate."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hashed_password",
            full_name="Test User",
        )

        assert aggregate.user.email_str == "test@example.com"
        assert aggregate.user.username_str == "testuser"
        assert aggregate.user.password == "hashed_password"
        assert aggregate.user.full_name == "Test User"
        assert aggregate.user.is_active is True

    def test_create_aggregate_generates_user_created_event(self):
        """Test that creating aggregate generates UserCreated event."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        events = aggregate.events
        assert len(events) == 1
        assert isinstance(events[0], UserCreated)
        assert events[0].email == "test@example.com"
        assert events[0].username == "testuser"

    def test_reconstitute_aggregate(self):
        """Test reconstituting aggregate from existing entity."""
        user = User(
            id=UserId.generate(),
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        aggregate = UserAggregate.reconstitute(user)

        assert aggregate.user == user
        assert len(aggregate.events) == 0  # No events when reconstituting

    def test_aggregate_id_property(self):
        """Test aggregate id property."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        assert isinstance(aggregate.id, UserId)
        assert aggregate.id == aggregate.user.id

    def test_aggregate_id_str_property(self):
        """Test aggregate id_str property."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        assert isinstance(aggregate.id_str, str)
        assert aggregate.id_str == aggregate.user.id_str

    def test_clear_events(self):
        """Test clearing events."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        assert len(aggregate.events) == 1

        aggregate.clear_events()

        assert len(aggregate.events) == 0

    def test_events_returns_copy(self):
        """Test that events property returns a copy."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        events1 = aggregate.events
        events2 = aggregate.events

        assert events1 is not events2
        assert events1 == events2

    def test_update_email(self):
        """Test updating email."""
        aggregate = UserAggregate.create(
            email=Email("old@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate.clear_events()

        aggregate.update_email(Email("new@example.com"))

        assert aggregate.user.email_str == "new@example.com"
        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserEmailUpdated)
        assert aggregate.events[0].old_email == "old@example.com"
        assert aggregate.events[0].new_email == "new@example.com"

    def test_update_email_inactive_user_raises_error(self):
        """Test that updating email on inactive user raises error."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate._user.is_active = False

        with pytest.raises(InvalidUserState) as exc_info:
            aggregate.update_email(Email("new@example.com"))

        assert "inactive" in str(exc_info.value).lower()

    def test_update_password(self):
        """Test updating password."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="old_hash",
        )
        aggregate.clear_events()

        aggregate.update_password("new_hash")

        assert aggregate.user.password == "new_hash"
        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserPasswordUpdated)

    def test_update_password_inactive_user_raises_error(self):
        """Test that updating password on inactive user raises error."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate._user.is_active = False

        with pytest.raises(InvalidUserState):
            aggregate.update_password("new_hash")

    def test_update_profile(self):
        """Test updating profile."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
            full_name="Old Name",
        )
        aggregate.clear_events()

        aggregate.update_profile(
            full_name="New Name",
            username=Username("newuser"),
        )

        assert aggregate.user.full_name == "New Name"
        assert aggregate.user.username_str == "newuser"
        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserUpdated)

    def test_update_profile_partial(self):
        """Test partial profile update."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate.clear_events()

        aggregate.update_profile(full_name="New Name")

        assert aggregate.user.full_name == "New Name"
        assert aggregate.user.username_str == "testuser"  # Unchanged

    def test_update_profile_no_changes_no_event(self):
        """Test that profile update with no changes generates no event."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate.clear_events()

        aggregate.update_profile()

        assert len(aggregate.events) == 0

    def test_update_profile_inactive_user_raises_error(self):
        """Test that updating profile on inactive user raises error."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate._user.is_active = False

        with pytest.raises(InvalidUserState):
            aggregate.update_profile(full_name="New Name")

    def test_deactivate(self):
        """Test deactivating user."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate.clear_events()

        aggregate.deactivate(reason="Test reason")

        assert aggregate.user.is_active is False
        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserDeactivated)
        assert aggregate.events[0].reason == "Test reason"

    def test_deactivate_already_inactive_raises_error(self):
        """Test that deactivating already inactive user raises error."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate._user.is_active = False

        with pytest.raises(InvalidUserState) as exc_info:
            aggregate.deactivate()

        assert "already inactive" in str(exc_info.value).lower()

    def test_activate(self):
        """Test activating user."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate._user.is_active = False
        aggregate.clear_events()

        aggregate.activate()

        assert aggregate.user.is_active is True
        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserActivated)

    def test_activate_already_active_raises_error(self):
        """Test that activating already active user raises error."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )

        with pytest.raises(InvalidUserState) as exc_info:
            aggregate.activate()

        assert "already active" in str(exc_info.value).lower()

    def test_soft_delete(self):
        """Test soft deleting user."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        deleter_id = UUID("12345678-1234-5678-1234-567812345678")
        aggregate.clear_events()

        aggregate.soft_delete(deleted_by=deleter_id)

        assert aggregate.user.is_deleted is True
        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserDeleted)
        assert aggregate.events[0].deleted_by == str(deleter_id)

    def test_soft_delete_without_deleted_by(self):
        """Test soft deleting without specifying who deleted."""
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password="hash",
        )
        aggregate.clear_events()

        aggregate.soft_delete()

        assert aggregate.user.is_deleted is True
        assert aggregate.events[0].deleted_by is None
