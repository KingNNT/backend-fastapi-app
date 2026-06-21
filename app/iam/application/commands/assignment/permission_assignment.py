"""Permission assignment commands."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AssignPermissionToUserCommand:
    """Command to assign a permission directly to a user."""

    user_id: str
    permission_id: str


@dataclass(frozen=True)
class RemovePermissionFromUserCommand:
    """Command to remove a direct permission from a user."""

    user_id: str
    permission_id: str


@dataclass(frozen=True)
class AssignPermissionToRoleCommand:
    """Command to assign a permission to a role."""

    role_id: str
    permission_id: str


@dataclass(frozen=True)
class RemovePermissionFromRoleCommand:
    """Command to remove a permission from a role."""

    role_id: str
    permission_id: str
