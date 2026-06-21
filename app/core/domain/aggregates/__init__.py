"""Aggregates - consistency boundaries for domain operations.

Only Log aggregate remains in core/. IAM aggregates live in app.iam.domain.
"""

from app.core.domain.aggregates.log import LogAggregate

__all__ = ["LogAggregate"]
