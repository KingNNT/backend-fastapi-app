"""Presentation-layer dependency providers for Log BC handlers only.

IAM-specific handler dependencies live in app.iam.presentation.dependencies.handlers.
"""

from typing import Annotated

from fastapi import Depends

from app.core.application.commands.handlers.log_handlers import CreateLogHandler
from app.core.application.queries.handlers.log_handlers import (
    GetLogByIdHandler,
    ListLogsByActionHandler,
    ListLogsByDateRangeHandler,
    ListLogsByUserHandler,
    ListLogsHandler,
)
from app.presentation.dependencies.repositories import (
    get_log_read_model_repository,
    get_log_repository,
)


# ─── Log Command Handlers ───────────────────────────────────────────────────
def get_create_log_handler(
    repository=Depends(get_log_repository),
) -> CreateLogHandler:
    """Get CreateLogHandler instance."""
    return CreateLogHandler(
        repository=repository,
        event_bus=None,  # Event bus injected at composition root
    )


# ─── Log Query Handlers ─────────────────────────────────────────────────────
def get_log_by_id_handler(
    repository=Depends(get_log_read_model_repository),
) -> GetLogByIdHandler:
    """Get GetLogByIdHandler instance."""
    return GetLogByIdHandler(repository=repository)


def get_list_logs_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsHandler:
    return ListLogsHandler(repository=repository)


def get_list_logs_by_user_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsByUserHandler:
    return ListLogsByUserHandler(repository=repository)


def get_list_logs_by_action_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsByActionHandler:
    return ListLogsByActionHandler(repository=repository)


def get_list_logs_by_date_range_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsByDateRangeHandler:
    return ListLogsByDateRangeHandler(repository=repository)


# ─── Type aliases ────────────────────────────────────────────────────────────
CreateLogHandlerDep = Annotated[CreateLogHandler, Depends(get_create_log_handler)]
GetLogByIdHandlerDep = Annotated[GetLogByIdHandler, Depends(get_log_by_id_handler)]
ListLogsHandlerDep = Annotated[ListLogsHandler, Depends(get_list_logs_handler)]
ListLogsByUserHandlerDep = Annotated[
    ListLogsByUserHandler, Depends(get_list_logs_by_user_handler)
]
