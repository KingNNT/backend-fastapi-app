"""IAM presentation dependency providers - Unit of Work + read-model repositories."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.iam.application.handlers.assignment_query_handlers import (
    IPermissionReadModelRepository,
    IRoleReadModelRepository,
)
from app.iam.application.handlers.user_query_handlers import (
    IUserReadModelRepository,
)
from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork
from app.iam.infrastructure.persistence.postgresql.repositories import (
    PostgresPermissionReadModelRepository,
    PostgresRoleReadModelRepository,
    PostgresUserReadModelRepository,
)
from app.iam.infrastructure.persistence.postgresql.unit_of_work import (
    PostgresIamUnitOfWork,
)
from app.platform.messaging.services import get_event_bus
from app.platform.persistence.postgresql import postgres_db_manager
from app.platform.persistence.postgresql.database import (
    get_postgres_session,
)


# ─── Unit of Work ─────────────────────────────────────────────────────────────
async def get_iam_unit_of_work() -> AsyncGenerator[IIamUnitOfWork, None]:
    """Request-scoped IAM UoW. Auto-commits on success, rollback on exception."""
    if postgres_db_manager.session_maker is None:
        raise RuntimeError(
            "Database is not connected. Call postgres_db_manager.connect() first."
        )
    uow = PostgresIamUnitOfWork(
        session_factory=postgres_db_manager.session_maker,
        event_bus=get_event_bus(),
    )
    async with uow:
        yield uow


IamUnitOfWorkDep = Annotated[IIamUnitOfWork, Depends(get_iam_unit_of_work)]


# ─── Read model repositories (no UoW needed - read-only) ────────────────────
async def get_user_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IUserReadModelRepository, None]:
    yield PostgresUserReadModelRepository(session)


UserReadModelRepositoryDep = Annotated[
    IUserReadModelRepository, Depends(get_user_read_model_repository)
]


async def get_role_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IRoleReadModelRepository, None]:
    yield PostgresRoleReadModelRepository(session)


RoleReadModelRepositoryDep = Annotated[
    IRoleReadModelRepository, Depends(get_role_read_model_repository)
]


async def get_permission_read_model_repository(
    session: AsyncSession = Depends(get_postgres_session),
) -> AsyncGenerator[IPermissionReadModelRepository, None]:
    yield PostgresPermissionReadModelRepository(session)


PermissionReadModelRepositoryDep = Annotated[
    IPermissionReadModelRepository, Depends(get_permission_read_model_repository)
]
