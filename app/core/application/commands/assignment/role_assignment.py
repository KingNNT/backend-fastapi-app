"""Role assignment commands."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AssignRoleToUserCommand:
    """Command to assign a role to a user."""

    user_id: str
    role_id: str


@dataclass(frozen=True)
class RemoveRoleFromUserCommand:
    """Command to remove a role from a user."""

    user_id: str
    role_id: str
