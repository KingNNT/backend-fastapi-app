"""User seeder for PostgreSQL database."""

import logging
from uuid import uuid4

from sqlmodel import func, select

from app.infrastructure.persistence.postgresql.database import postgres_db_manager
from app.infrastructure.persistence.postgresql.models.user import UserModel

logger = logging.getLogger(__name__)


class UserSeeder:
    """Seeder for User entity in PostgreSQL."""

    def __init__(self, use_test_db: bool = False):
        """Initialize the seeder.

        Args:
            use_test_db: If True, use test database instead of development.
        """
        self._use_test_db = use_test_db

    @property
    def entity_name(self) -> str:
        """Return the entity name."""
        return "user"

    @property
    def database_type(self) -> str:
        """Return database type."""
        return "postgresql"

    async def seed(self, count: int = 10, dry_run: bool = False) -> int:
        """Seed user data.

        Args:
            count: Number of users to seed.
            dry_run: If True, preview without making changes.

        Returns:
            Number of seeded records.
        """
        if dry_run:
            logger.info(f"[DRY RUN] Would seed {count} users")
            return count

        await postgres_db_manager.connect(use_test_db=self._use_test_db)
        try:
            if postgres_db_manager.session_maker is None:
                raise RuntimeError("Database session maker is not initialized")

            async with postgres_db_manager.session_maker() as session:
                # Check existing users to avoid duplicates
                result = await session.execute(
                    select(func.count(UserModel.id))  # type: ignore[arg-type]
                )
                existing_count = result.scalar() or 0

                if existing_count > 0:
                    logger.warning(
                        f"Found {existing_count} existing users. "
                        "Generating unique data to avoid conflicts."
                    )

                # Generate sample users
                users_to_create = []
                for i in range(count):
                    unique_id = uuid4().hex[:8]
                    user = UserModel(
                        email=f"user_{unique_id}@example.com",
                        username=f"user_{unique_id}",
                        password=f"hashed_password_{unique_id}",
                        full_name=f"Test User {i + 1}",
                        is_active=True,
                    )
                    users_to_create.append(user)

                # Add users to session
                for user in users_to_create:
                    session.add(user)

                await session.commit()
                logger.info(f"Successfully seeded {len(users_to_create)} users")
                return len(users_to_create)
        finally:
            await postgres_db_manager.close()

    async def clear(self, dry_run: bool = False) -> int:
        """Clear all user data.

        Args:
            dry_run: If True, preview without making changes.

        Returns:
            Number of cleared records.
        """
        await postgres_db_manager.connect(use_test_db=self._use_test_db)
        try:
            if postgres_db_manager.session_maker is None:
                raise RuntimeError("Database session maker is not initialized")

            async with postgres_db_manager.session_maker() as session:
                # Count users first
                result = await session.execute(
                    select(func.count(UserModel.id))  # type: ignore[arg-type]
                )
                user_count = result.scalar() or 0

                if dry_run:
                    logger.info(f"[DRY RUN] Would clear {user_count} users")
                    return user_count

                if user_count == 0:
                    logger.info("No users to clear")
                    return 0

                # Delete all users
                result = await session.execute(select(UserModel))
                users = result.scalars().all()

                for user in users:
                    await session.delete(user)

                await session.commit()
                logger.info(f"Cleared {user_count} users")
                return user_count
        finally:
            await postgres_db_manager.close()

    async def count(self) -> int:
        """Count existing users.

        Returns:
            Current number of users in the database.
        """
        await postgres_db_manager.connect(use_test_db=self._use_test_db)
        try:
            if postgres_db_manager.session_maker is None:
                raise RuntimeError("Database session maker is not initialized")

            async with postgres_db_manager.session_maker() as session:
                result = await session.execute(
                    select(func.count(UserModel.id))  # type: ignore[arg-type]
                )
                return result.scalar() or 0
        finally:
            await postgres_db_manager.close()
