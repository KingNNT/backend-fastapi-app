"""List logs query."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ListLogsQuery:
    """Query to list logs with pagination."""

    skip: int = 0
    limit: int = 100


@dataclass(frozen=True)
class ListLogsByUserQuery:
    """Query to list logs for a specific user."""

    user_id: str
    skip: int = 0
    limit: int = 100


@dataclass(frozen=True)
class ListLogsByActionQuery:
    """Query to list logs by action type."""

    action: str
    skip: int = 0
    limit: int = 100


@dataclass(frozen=True)
class ListLogsByDateRangeQuery:
    """Query to list logs within a date range."""

    start_date: datetime
    end_date: datetime
    skip: int = 0
    limit: int = 100
