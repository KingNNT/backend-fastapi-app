from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.configs.app import get_app_config


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_maker = None

    async def connect(self):
        """Initialize PostgreSQL connection and SQLModel."""
        config = get_app_config()

        # Create async engine for PostgreSQL
        self.engine = create_async_engine(
            config.postgre_database_url,
            echo=config.debug,  # Log SQL queries in debug mode
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        # Create session maker
        self.session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def close(self):
        """Close PostgreSQL connection."""
        if self.engine:
            await self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


async def get_database():
    """Get database session (for dependency injection)."""
    if db_manager.session_maker is None:
        raise RuntimeError(
            "Database is not connected. Call db_manager.connect() first."
        )

    async with db_manager.session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
