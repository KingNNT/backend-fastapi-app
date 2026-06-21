"""Entities - objects with identity.

Only Log entity remains. IAM ones live in app.iam.domain.<aggregate>.entity.
"""

from app.core.domain.entities.log import Log

__all__ = ["Log"]
