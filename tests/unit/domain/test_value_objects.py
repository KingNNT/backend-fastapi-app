"""Unit tests for domain value objects."""

from uuid import UUID

import pytest

from app.iam.domain.user.value_objects import Email, Username
from app.shared.domain.ids import UserId


class TestEmail:
    """Tests for Email value object."""

    def test_create_valid_email(self):
        """Test creating a valid email."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"
        assert str(email) == "test@example.com"

    def test_create_email_with_subdomain(self):
        """Test creating email with subdomain."""
        email = Email("user@mail.example.com")
        assert email.value == "user@mail.example.com"

    def test_create_email_with_plus_sign(self):
        """Test creating email with plus sign."""
        email = Email("user+tag@example.com")
        assert email.value == "user+tag@example.com"

    def test_invalid_email_no_at_sign(self):
        """Test that email without @ raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email"):
            Email("invalidemail.com")

    def test_invalid_email_no_domain(self):
        """Test that email without domain raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email"):
            Email("user@")

    def test_invalid_email_no_tld(self):
        """Test that email without TLD raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email"):
            Email("user@domain")

    def test_invalid_email_empty(self):
        """Test that empty email raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email"):
            Email("")

    def test_email_equality(self):
        """Test that emails with same value are equal."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        assert email1 == email2

    def test_email_inequality(self):
        """Test that emails with different values are not equal."""
        email1 = Email("test1@example.com")
        email2 = Email("test2@example.com")
        assert email1 != email2

    def test_email_is_immutable(self):
        """Test that Email is immutable (frozen dataclass)."""
        email = Email("test@example.com")
        with pytest.raises(AttributeError):
            email.value = "new@example.com"


class TestUsername:
    """Tests for Username value object."""

    def test_create_valid_username(self):
        """Test creating a valid username."""
        username = Username("testuser")
        assert username.value == "testuser"
        assert str(username) == "testuser"

    def test_create_username_with_numbers(self):
        """Test creating username with numbers."""
        username = Username("user123")
        assert username.value == "user123"

    def test_create_username_with_underscore(self):
        """Test creating username with underscore."""
        username = Username("test_user")
        assert username.value == "test_user"

    def test_create_username_with_hyphen(self):
        """Test creating username with hyphen."""
        username = Username("test-user")
        assert username.value == "test-user"

    def test_invalid_username_too_short(self):
        """Test that username too short raises ValueError."""
        with pytest.raises(ValueError, match="Invalid username"):
            Username("ab")

    def test_invalid_username_starts_with_number(self):
        """Test that username starting with number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid username"):
            Username("1user")

    def test_invalid_username_special_chars(self):
        """Test that username with special chars raises ValueError."""
        with pytest.raises(ValueError, match="Invalid username"):
            Username("user@name")

    def test_invalid_username_empty(self):
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="Invalid username"):
            Username("")

    def test_username_minimum_length(self):
        """Test username at minimum length (3 chars)."""
        username = Username("abc")
        assert username.value == "abc"

    def test_username_equality(self):
        """Test that usernames with same value are equal."""
        username1 = Username("testuser")
        username2 = Username("testuser")
        assert username1 == username2

    def test_username_inequality(self):
        """Test that usernames with different values are not equal."""
        username1 = Username("user1")
        username2 = Username("user2")
        assert username1 != username2

    def test_username_is_immutable(self):
        """Test that Username is immutable (frozen dataclass)."""
        username = Username("testuser")
        with pytest.raises(AttributeError):
            username.value = "newuser"


class TestUserId:
    """Tests for UserId value object."""

    def test_create_user_id_from_uuid(self):
        """Test creating UserId from UUID."""
        uuid = UUID("12345678-1234-5678-1234-567812345678")
        user_id = UserId(value=uuid)
        assert user_id.value == uuid

    def test_generate_user_id(self):
        """Test generating a new UserId."""
        user_id = UserId.generate()
        assert isinstance(user_id.value, UUID)

    def test_generate_unique_ids(self):
        """Test that generated IDs are unique."""
        id1 = UserId.generate()
        id2 = UserId.generate()
        assert id1 != id2

    def test_user_id_str(self):
        """Test UserId string representation."""
        uuid = UUID("12345678-1234-5678-1234-567812345678")
        user_id = UserId(value=uuid)
        assert str(user_id) == "12345678-1234-5678-1234-567812345678"

    def test_user_id_from_string(self):
        """Test creating UserId from string."""
        user_id = UserId.from_string("12345678-1234-5678-1234-567812345678")
        assert str(user_id) == "12345678-1234-5678-1234-567812345678"

    def test_user_id_from_invalid_string(self):
        """Test that invalid UUID string raises ValueError."""
        with pytest.raises(ValueError):
            UserId.from_string("invalid-uuid")

    def test_user_id_equality(self):
        """Test that UserIds with same value are equal."""
        uuid = UUID("12345678-1234-5678-1234-567812345678")
        id1 = UserId(value=uuid)
        id2 = UserId(value=uuid)
        assert id1 == id2

    def test_user_id_inequality(self):
        """Test that UserIds with different values are not equal."""
        id1 = UserId.generate()
        id2 = UserId.generate()
        assert id1 != id2

    def test_user_id_is_immutable(self):
        """Test that UserId is immutable (frozen dataclass)."""
        user_id = UserId.generate()
        with pytest.raises(AttributeError):
            user_id.value = UUID("12345678-1234-5678-1234-567812345678")
