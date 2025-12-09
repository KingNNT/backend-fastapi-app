"""Dependency injection for CQRS handlers."""

from typing import Annotated

from fastapi import Depends

from app.core.application.commands.handlers import (
    CreateLogHandler,
    CreateUserHandler,
    DeleteUserHandler,
    UpdateUserHandler,
)
from app.core.application.queries.handlers import (
    GetLogByIdHandler,
    GetUserByEmailHandler,
    GetUserByIdHandler,
    GetUserByUsernameHandler,
    ListLogsByUserHandler,
    ListLogsHandler,
    ListUsersHandler,
)
from app.presentation.dependencies.repositories import (
    get_log_read_model_repository,
    get_log_repository,
    get_user_read_model_repository,
    get_user_repository,
)
from app.presentation.dependencies.services import (
    get_event_bus,
    get_password_hasher,
    get_user_domain_service,
)


# User Command Handlers
def get_create_user_handler(
    repository=Depends(get_user_repository),
    domain_service=Depends(get_user_domain_service),
    event_bus=Depends(get_event_bus),
    password_hasher=Depends(get_password_hasher),
) -> CreateUserHandler:
    """Get CreateUserHandler instance."""
    return CreateUserHandler(
        repository=repository,
        domain_service=domain_service,
        event_bus=event_bus,
        password_hasher=password_hasher,
    )


def get_update_user_handler(
    repository=Depends(get_user_repository),
    domain_service=Depends(get_user_domain_service),
    event_bus=Depends(get_event_bus),
    password_hasher=Depends(get_password_hasher),
) -> UpdateUserHandler:
    """Get UpdateUserHandler instance."""
    return UpdateUserHandler(
        repository=repository,
        domain_service=domain_service,
        event_bus=event_bus,
        password_hasher=password_hasher,
    )


def get_delete_user_handler(
    repository=Depends(get_user_repository),
    event_bus=Depends(get_event_bus),
) -> DeleteUserHandler:
    """Get DeleteUserHandler instance."""
    return DeleteUserHandler(
        repository=repository,
        event_bus=event_bus,
    )


# User Query Handlers
def get_user_by_id_handler(
    repository=Depends(get_user_read_model_repository),
) -> GetUserByIdHandler:
    """Get GetUserByIdHandler instance."""
    return GetUserByIdHandler(repository=repository)


def get_user_by_email_handler(
    repository=Depends(get_user_read_model_repository),
) -> GetUserByEmailHandler:
    """Get GetUserByEmailHandler instance."""
    return GetUserByEmailHandler(repository=repository)


def get_user_by_username_handler(
    repository=Depends(get_user_read_model_repository),
) -> GetUserByUsernameHandler:
    """Get GetUserByUsernameHandler instance."""
    return GetUserByUsernameHandler(repository=repository)


def get_list_users_handler(
    repository=Depends(get_user_read_model_repository),
) -> ListUsersHandler:
    """Get ListUsersHandler instance."""
    return ListUsersHandler(repository=repository)


# Log Command Handlers
def get_create_log_handler(
    repository=Depends(get_log_repository),
    event_bus=Depends(get_event_bus),
) -> CreateLogHandler:
    """Get CreateLogHandler instance."""
    return CreateLogHandler(
        repository=repository,
        event_bus=event_bus,
    )


# Log Query Handlers
def get_log_by_id_handler(
    repository=Depends(get_log_read_model_repository),
) -> GetLogByIdHandler:
    """Get GetLogByIdHandler instance."""
    return GetLogByIdHandler(repository=repository)


def get_list_logs_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsHandler:
    """Get ListLogsHandler instance."""
    return ListLogsHandler(repository=repository)


def get_list_logs_by_user_handler(
    repository=Depends(get_log_read_model_repository),
) -> ListLogsByUserHandler:
    """Get ListLogsByUserHandler instance."""
    return ListLogsByUserHandler(repository=repository)


# Type aliases for dependency injection
CreateUserHandlerDep = Annotated[CreateUserHandler, Depends(get_create_user_handler)]
UpdateUserHandlerDep = Annotated[UpdateUserHandler, Depends(get_update_user_handler)]
DeleteUserHandlerDep = Annotated[DeleteUserHandler, Depends(get_delete_user_handler)]
GetUserByIdHandlerDep = Annotated[GetUserByIdHandler, Depends(get_user_by_id_handler)]
GetUserByEmailHandlerDep = Annotated[
    GetUserByEmailHandler, Depends(get_user_by_email_handler)
]
GetUserByUsernameHandlerDep = Annotated[
    GetUserByUsernameHandler, Depends(get_user_by_username_handler)
]
ListUsersHandlerDep = Annotated[ListUsersHandler, Depends(get_list_users_handler)]
CreateLogHandlerDep = Annotated[CreateLogHandler, Depends(get_create_log_handler)]
GetLogByIdHandlerDep = Annotated[GetLogByIdHandler, Depends(get_log_by_id_handler)]
ListLogsHandlerDep = Annotated[ListLogsHandler, Depends(get_list_logs_handler)]
ListLogsByUserHandlerDep = Annotated[
    ListLogsByUserHandler, Depends(get_list_logs_by_user_handler)
]
