"""Get log query."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetLogByIdQuery:
    """Query to get a log by ID."""

    log_id: str
