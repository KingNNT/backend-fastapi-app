"""Get permission query."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetPermissionByIdQuery:
    """Query to get a permission by ID."""

    permission_id: str


@dataclass(frozen=True)
class GetPermissionByNameQuery:
    """Query to get a permission by name."""

    name: str
