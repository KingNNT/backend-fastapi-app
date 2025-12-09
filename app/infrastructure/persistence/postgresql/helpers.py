"""PostgreSQL persistence helpers."""

from datetime import datetime
from typing import Optional


def strip_timezone(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Strip timezone info from datetime for PostgreSQL compatibility.

    PostgreSQL TIMESTAMP WITHOUT TIME ZONE columns don't accept
    timezone-aware datetimes. This helper converts them to naive UTC.
    """
    if dt is None:
        return None
    return dt.replace(tzinfo=None) if dt.tzinfo else dt
