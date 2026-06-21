"""Presentation layer dependencies — Log BC only.

IAM-specific dependencies live in app.iam.presentation.dependencies.
"""

from app.presentation.dependencies.handlers import (
    CreateLogHandlerDep,
    GetLogByIdHandlerDep,
    ListLogsByUserHandlerDep,
    ListLogsHandlerDep,
    get_create_log_handler,
    get_list_logs_by_user_handler,
    get_list_logs_handler,
    get_log_by_id_handler,
)
from app.presentation.dependencies.repositories import (
    PostgresSessionDep,
    get_log_read_model_repository,
    get_log_repository,
    set_log_read_model_repository,
    set_log_repository,
)

__all__ = [
    # Repository providers (MongoDB - app-scoped)
    "get_log_repository",
    "get_log_read_model_repository",
    "set_log_repository",
    "set_log_read_model_repository",
    # Session dep
    "PostgresSessionDep",
    # Handler factories (Log)
    "get_create_log_handler",
    "get_log_by_id_handler",
    "get_list_logs_handler",
    "get_list_logs_by_user_handler",
    # Log handler type aliases
    "CreateLogHandlerDep",
    "GetLogByIdHandlerDep",
    "ListLogsHandlerDep",
    "ListLogsByUserHandlerDep",
]
