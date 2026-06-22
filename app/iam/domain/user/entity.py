"""User entity - represents a user in the domain."""

from dataclasses import dataclass, field
from typing import Optional

from app.iam.domain.user.value_objects import Email, Username
from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.ids.user_id import UserId


@dataclass
class User(BaseEntity):
    """
    User entity with identity.
    Stored in PostgreSQL.
    """

    id: UserId = field(default_factory=UserId.generate)
    email: Email = field(default_factory=lambda: Email("default@example.com"))
    username: Username = field(default_factory=lambda: Username("default_user"))
    password: str = ""
    full_name: Optional[str] = None
    is_active: bool = True

    def __post_init__(self) -> None:
        # Ensure value objects are properly typed
        if isinstance(self.email, str):
            object.__setattr__(self, "email", Email(self.email))
        if isinstance(self.username, str):
            object.__setattr__(self, "username", Username(self.username))
        if isinstance(self.id, str):
            object.__setattr__(self, "id", UserId.from_string(self.id))

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.mark_updated()

    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True
        self.mark_updated()

    def update_email(self, new_email: Email) -> None:
        """Update user's email."""
        self.email = new_email
        self.mark_updated()

    def update_password(self, new_password: str) -> None:
        """Update user's password."""
        self.password = new_password
        self.mark_updated()

    def update_profile(
        self,
        full_name: Optional[str] = None,
        username: Optional[Username] = None,
    ) -> None:
        """Update user's profile information."""
        if full_name is not None:
            self.full_name = full_name
        if username is not None:
            self.username = username
        self.mark_updated()

    @property
    def email_str(self) -> str:
        """Get email as string."""
        return str(self.email)

    @property
    def username_str(self) -> str:
        """Get username as string."""
        return str(self.username)

    @property
    def id_str(self) -> str:
        """Get id as string."""
        return str(self.id)
