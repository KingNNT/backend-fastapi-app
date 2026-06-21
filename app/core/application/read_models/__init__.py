"""Read models - optimized for queries (CQRS query side).

Only Log read model remains. IAM ones live in app.iam.application.read_models.
"""

from app.core.application.read_models.log_read_model import LogReadModel

__all__ = ["LogReadModel"]
