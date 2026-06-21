"""Command handlers - execute write operations.

Only Log handler remains in core/. IAM handlers live in app.iam.application.handlers.
"""

from app.core.application.commands.handlers.log_handlers import CreateLogHandler

__all__ = ["CreateLogHandler"]
