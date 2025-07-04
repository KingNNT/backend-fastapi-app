from contextlib import asynccontextmanager
from typing import AsyncGenerator

import motor.motor_asyncio
from beanie import init_beanie

from app.configs.app import get_app_config
from app.internal.models.user import User


class DatabaseManager:
    def __init__(self):
        self.client: motor.motor_asyncio.AsyncIOMotorClient | None = None
        self.database = None

    async def connect(self):
        """Initialize MongoDB connection and Beanie ODM."""
        config = get_app_config()

        # Create MongoDB client
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.mongodb_url)
        self.database = self.client[config.mongodb_database]

        # Initialize Beanie with document models
        await init_beanie(database=self.database, document_models=[User])

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


# Global database manager instance
db_manager = DatabaseManager()


async def get_database():
    """Get database instance (for dependency injection)."""
    return db_manager.database


@asynccontextmanager
async def database_lifespan(app) -> AsyncGenerator[None, None]:
    """Database lifespan context manager for FastAPI."""
    # Startup
    await db_manager.connect()
    yield
    # Shutdown
    await db_manager.close()
