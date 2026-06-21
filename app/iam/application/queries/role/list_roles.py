"""List roles query."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ListRolesQuery:
    """Query to list roles with pagination."""

    skip: int = 0
    limit: int = 100
    include_deleted: bool = False
