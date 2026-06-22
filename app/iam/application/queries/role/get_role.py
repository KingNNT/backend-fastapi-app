"""Get role query."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetRoleByIdQuery:
    """Query to get a role by ID."""

    role_id: str


@dataclass(frozen=True)
class GetRoleByNameQuery:
    """Query to get a role by name."""

    name: str
