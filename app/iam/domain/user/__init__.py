"""User aggregate — domain layer for User concept."""

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
from app.iam.domain.user.exceptions import (
    InvalidUserState,
    UserAlreadyExists,
    UserNotFound,
)
from app.iam.domain.user.repository import (
    IUserReadRepository,
    IUserWriteRepository,
)
from app.iam.domain.user.value_objects import Email, Username

__all__ = [
    "UserAggregate",
    "User",
    "Email",
    "Username",
    "UserCreated",
    "UserUpdated",
    "UserDeleted",
    "UserDeactivated",
    "UserActivated",
    "UserEmailUpdated",
    "UserPasswordUpdated",
    "UserNotFound",
    "UserAlreadyExists",
    "InvalidUserState",
    "IUserWriteRepository",
    "IUserReadRepository",
]
