"""Action value object - represents a log action type."""

from dataclasses import dataclass
from enum import Enum


class ActionType(str, Enum):
    """Predefined action types for logging."""

    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    CUSTOM = "custom"


@dataclass(frozen=True)
class Action:
    """
    Action value object.
    Represents the type of action being logged.
    Immutable and self-validating.
    """

    value: str
    action_type: ActionType = ActionType.CUSTOM

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Action value must be a non-empty string")
        if len(self.value) > 255:
            raise ValueError("Action value must be 255 characters or less")

    @classmethod
    def user_created(cls) -> "Action":
        """Create a user_created action."""
        return cls(
            value=ActionType.USER_CREATED.value, action_type=ActionType.USER_CREATED
        )

    @classmethod
    def user_updated(cls) -> "Action":
        """Create a user_updated action."""
        return cls(
            value=ActionType.USER_UPDATED.value, action_type=ActionType.USER_UPDATED
        )

    @classmethod
    def user_deleted(cls) -> "Action":
        """Create a user_deleted action."""
        return cls(
            value=ActionType.USER_DELETED.value, action_type=ActionType.USER_DELETED
        )

    @classmethod
    def custom(cls, value: str) -> "Action":
        """Create a custom action."""
        return cls(value=value, action_type=ActionType.CUSTOM)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Action):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)
