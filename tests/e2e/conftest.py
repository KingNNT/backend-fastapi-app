"""E2E test fixtures using test databases on running Docker services.

This conftest uses Option 1 for test databases: separate database names
on the same running Docker containers (not testcontainers).

Prerequisites:
- Docker services must be running: `make db-up`
- Test databases will be created automatically if they don't exist
"""

import asyncio
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.infrastructure.persistence.mongodb.database import mongo_db_manager
from app.infrastructure.persistence.mongodb.models.log import LogModel
from app.infrastructure.persistence.postgresql.database import postgres_db_manager
from app.infrastructure.persistence.postgresql.models import UserModel
from app.infrastructure.setup import setup_app_services
from app.infrastructure.web import register_exception_handlers
from app.presentation.api import api_router

# Mark all tests in this directory as e2e tests
pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def event_loop():
    """Create session-scoped event loop for async fixtures."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_test_databases():
    """Initialize test database connections for the session.

    Connects to test databases on the running Docker services.
    Creates tables if they don't exist.
    """
    # Connect to test databases
    await postgres_db_manager.connect(use_test_db=True)
    await mongo_db_manager.connect(use_test_db=True)

    # Create tables in test database
    if postgres_db_manager.engine is not None:
        async with postgres_db_manager.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    # Set up app-scoped services (event bus, password hasher, MongoDB repos)
    setup_app_services()

    yield

    # Cleanup: close connections
    await postgres_db_manager.close()
    await mongo_db_manager.close()


@pytest.fixture(scope="session")
async def test_app(setup_test_databases) -> AsyncGenerator[FastAPI, None]:
    """Create test FastAPI application with real test databases.

    PostgreSQL repositories are request-scoped via Depends(get_postgres_session),
    so they automatically use the test database connection.
    """
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(api_router)

    yield app


@pytest.fixture
async def clean_databases(setup_test_databases):
    """Clean test databases before and after each test."""
    # Clean PostgreSQL
    if postgres_db_manager.session_maker is not None:
        async with postgres_db_manager.session_maker() as session:
            await session.execute(UserModel.__table__.delete())
            await session.commit()

    # Clean MongoDB
    await LogModel.delete_all()

    yield

    # Clean after test
    if postgres_db_manager.session_maker is not None:
        async with postgres_db_manager.session_maker() as session:
            await session.execute(UserModel.__table__.delete())
            await session.commit()

    await LogModel.delete_all()


@pytest.fixture
def client(test_app: FastAPI, clean_databases) -> TestClient:
    """Create sync test client with clean databases."""
    return TestClient(test_app)


@pytest.fixture
async def async_client(
    test_app: FastAPI, clean_databases
) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with clean databases."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def postgres_session(setup_test_databases) -> AsyncGenerator[AsyncSession, None]:
    """Get PostgreSQL session for direct database operations in tests."""
    if postgres_db_manager.session_maker is None:
        raise RuntimeError("PostgreSQL session maker is not initialized")

    async with postgres_db_manager.session_maker() as session:
        yield session
        await session.rollback()
