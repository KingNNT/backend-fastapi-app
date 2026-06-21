"""PostgreSQL database manager."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.platform.configs import get_app_config


class PostgresDatabaseManager:
    """Manages PostgreSQL database connections."""

    def __init__(self):
        self.engine = None
        self.session_maker = None
        self._is_test_mode = False

    async def connect(self, *, use_test_db: bool = False):
        """Initialize PostgreSQL connection.

        Args:
            use_test_db: If True, connect to the test database instead of
                the main database.
        """
        config = get_app_config()
        self._is_test_mode = use_test_db

        # Select the appropriate database URL
        database_url = (
            config.postgre_test_database_url
            if use_test_db
            else config.postgre_database_url
        )

        # Create async engine for PostgreSQL
        self.engine = create_async_engine(
            database_url,
            echo=config.debug,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        # Create session maker
        self.session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    @property
    def is_test_mode(self) -> bool:
        """Check if connected to test database."""
        return self._is_test_mode

    async def close(self):
        """Close PostgreSQL connection."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None
            self._is_test_mode = False


# Global database manager instance
postgres_db_manager = PostgresDatabaseManager()


async def get_postgres_session():
    """Get database session (for dependency injection)."""
    if postgres_db_manager.session_maker is None:
        raise RuntimeError(
            "Database is not connected. Call postgres_db_manager.connect() first."
        )

    async with postgres_db_manager.session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
