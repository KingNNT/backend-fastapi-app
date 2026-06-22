"""Audit presentation dependency providers."""

from app.audit.presentation.dependencies.handlers import (
    CreateLogHandlerDep,
    GetLogByIdHandlerDep,
    ListLogsByActionHandlerDep,
    ListLogsByDateRangeHandlerDep,
    ListLogsByUserHandlerDep,
    ListLogsHandlerDep,
    get_create_log_handler,
    get_list_logs_by_action_handler,
    get_list_logs_by_date_range_handler,
    get_list_logs_by_user_handler,
    get_list_logs_handler,
    get_log_by_id_handler,
)
from app.audit.presentation.dependencies.repositories import (
    get_log_read_model_repository,
    get_log_repository,
    set_log_read_model_repository,
    set_log_repository,
)

__all__ = [
    # Repository providers
    "get_log_repository",
    "get_log_read_model_repository",
    "set_log_repository",
    "set_log_read_model_repository",
    # Handler providers
    "get_create_log_handler",
    "get_log_by_id_handler",
    "get_list_logs_handler",
    "get_list_logs_by_user_handler",
    "get_list_logs_by_action_handler",
    "get_list_logs_by_date_range_handler",
    # Type aliases
    "CreateLogHandlerDep",
    "GetLogByIdHandlerDep",
    "ListLogsHandlerDep",
    "ListLogsByUserHandlerDep",
    "ListLogsByActionHandlerDep",
    "ListLogsByDateRangeHandlerDep",
]
