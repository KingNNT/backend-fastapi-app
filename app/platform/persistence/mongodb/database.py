"""MongoDB database manager."""

import motor.motor_asyncio
from beanie import init_beanie

from app.audit.infrastructure.persistence.mongodb.models.log import LogModel
from app.platform.configs import get_app_config


class MongoDatabaseManager:
    """Manages MongoDB database connections."""

    def __init__(self):
        self.client: motor.motor_asyncio.AsyncIOMotorClient | None = None
        self.database = None
        self._is_test_mode = False

    async def connect(self, *, use_test_db: bool = False):
        """Initialize MongoDB connection and Beanie ODM.

        Args:
            use_test_db: If True, connect to the test database instead of
                the main database.
        """
        config = get_app_config()
        self._is_test_mode = use_test_db

        # Create MongoDB client
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.mongodb_url)

        # Select the appropriate database
        database_name = (
            config.mongodb_test_database if use_test_db else config.mongodb_database
        )
        self.database = self.client[database_name]

        # Initialize Beanie with document models
        await init_beanie(database=self.database, document_models=[LogModel])

    @property
    def is_test_mode(self) -> bool:
        """Check if connected to test database."""
        return self._is_test_mode

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self._is_test_mode = False


# Global database manager instance
mongo_db_manager = MongoDatabaseManager()


async def get_mongo_database():
    """Get database instance (for dependency injection)."""
    return mongo_db_manager.database
