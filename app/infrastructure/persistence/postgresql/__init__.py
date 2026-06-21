"""PostgreSQL persistence layer.

IAM-specific code (models, mappers, repositories, unit_of_work) has moved to
app.iam.infrastructure. This module is kept for Alembic migration imports and
the helpers utility (strip_timezone), which is generic.
"""

# Helpers moved to IAM but it's a generic utility used by other code.
# Keep a re-export here for backward compatibility.
from app.iam.infrastructure.persistence.postgresql.helpers import strip_timezone

__all__ = ["strip_timezone"]
