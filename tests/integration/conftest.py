"""Integration test fixtures with real databases using testcontainers."""

import asyncio
from typing import AsyncGenerator

import motor.motor_asyncio
import pytest
from beanie import init_beanie
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from testcontainers.mongodb import MongoDbContainer
from testcontainers.postgres import PostgresContainer

from app.iam.infrastructure.persistence.postgresql.models.user import UserModel
from app.infrastructure.persistence.mongodb.models.log import LogModel

# Mark all integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def event_loop():
    """Create session-scoped event loop for async fixtures."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    """Start PostgreSQL container for the test session."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def mongodb_container():
    """Start MongoDB container for the test session."""
    with MongoDbContainer("mongo:7.0") as mongo:
        yield mongo


@pytest.fixture(scope="session")
async def postgres_engine(postgres_container):
    """Create async PostgreSQL engine."""
    connection_url = postgres_container.get_connection_url()
    # Convert to asyncpg URL format (handle both postgresql:// and postgresql+psycopg2://)
    async_url = connection_url.replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )
    async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(
        async_url,
        echo=False,
        pool_pre_ping=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def postgres_session(postgres_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create PostgreSQL session for each test with automatic cleanup."""
    session_maker = async_sessionmaker(
        postgres_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_maker() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()

    # Clean up data after each test
    async with session_maker() as cleanup_session:
        await cleanup_session.execute(UserModel.__table__.delete())
        await cleanup_session.commit()


@pytest.fixture(scope="session")
async def mongodb_client(mongodb_container):
    """Create MongoDB client."""
    connection_url = mongodb_container.get_connection_url()
    client = motor.motor_asyncio.AsyncIOMotorClient(connection_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
async def mongodb_database(mongodb_client):
    """Get MongoDB database with Beanie initialized."""
    database = mongodb_client["test_database"]

    # Initialize Beanie with LogModel
    await init_beanie(database=database, document_models=[LogModel])

    yield database


@pytest.fixture
async def clean_mongodb(mongodb_database):
    """Clean MongoDB collection before and after each test."""
    # Clean before test
    await LogModel.delete_all()

    yield mongodb_database

    # Clean after test
    await LogModel.delete_all()
