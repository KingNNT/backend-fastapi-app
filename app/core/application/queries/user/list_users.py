"""List users query."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListUsersQuery:
    """Query to list users with pagination and filtering."""

    skip: int = 0
    limit: int = 100
    email: Optional[str] = None
    username: Optional[str] = None
    include_deleted: bool = False
