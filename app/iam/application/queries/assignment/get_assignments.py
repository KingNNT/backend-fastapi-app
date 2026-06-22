"""Assignment queries."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserRolesQuery:
    """Query to get all roles assigned to a user."""

    user_id: str


@dataclass(frozen=True)
class GetUserEffectivePermissionsQuery:
    """Query to get all effective permissions for a user.

    This includes direct permissions and permissions from assigned roles.
    """

    user_id: str


@dataclass(frozen=True)
class GetRolePermissionsQuery:
    """Query to get all permissions assigned to a role."""

    role_id: str
