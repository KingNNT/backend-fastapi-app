"""User-specific specifications for business rules."""

from app.core.domain.entities.user import User
from app.core.domain.specifications.base import Specification


class ActiveUserSpecification(Specification[User]):
    """Specification that checks if a user is active."""

    def is_satisfied_by(self, user: User) -> bool:
        return user.is_active and user.deleted_at is None


class NotDeletedUserSpecification(Specification[User]):
    """Specification that checks if a user is not soft-deleted."""

    def is_satisfied_by(self, user: User) -> bool:
        return user.deleted_at is None


class HasFullNameSpecification(Specification[User]):
    """Specification that checks if a user has a full name."""

    def is_satisfied_by(self, user: User) -> bool:
        return user.full_name is not None and len(user.full_name.strip()) > 0


class UniqueEmailSpecification(Specification[str]):
    """
    Specification that checks if an email is unique.
    Requires a set of existing emails to check against.
    """

    def __init__(self, existing_emails: set[str]) -> None:
        self._existing_emails = existing_emails

    def is_satisfied_by(self, email: str) -> bool:
        return email.lower() not in {e.lower() for e in self._existing_emails}


class UniqueUsernameSpecification(Specification[str]):
    """
    Specification that checks if a username is unique.
    Requires a set of existing usernames to check against.
    """

    def __init__(self, existing_usernames: set[str]) -> None:
        self._existing_usernames = existing_usernames

    def is_satisfied_by(self, username: str) -> bool:
        return username.lower() not in {u.lower() for u in self._existing_usernames}


class CanUpdateUserSpecification(Specification[User]):
    """
    Composite specification that checks if a user can be updated.
    User must be active and not deleted.
    """

    def is_satisfied_by(self, user: User) -> bool:
        active_spec = ActiveUserSpecification()
        not_deleted_spec = NotDeletedUserSpecification()
        combined = active_spec.and_(not_deleted_spec)
        return combined.is_satisfied_by(user)
