"""Domain events - records of things that happened in the domain.

Only Log events remain in core/. IAM events live in app.iam.domain.<aggregate>.events.
"""

from app.core.domain.events.log_events import LogCreated

__all__ = ["LogCreated"]
