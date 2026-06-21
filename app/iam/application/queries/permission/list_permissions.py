"""List permissions query."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ListPermissionsQuery:
    """Query to list permissions with pagination."""

    skip: int = 0
    limit: int = 100
    include_deleted: bool = False
