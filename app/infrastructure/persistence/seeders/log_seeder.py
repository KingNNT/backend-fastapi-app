"""Log seeder for MongoDB database."""

import logging
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.infrastructure.persistence.mongodb.database import mongo_db_manager
from app.infrastructure.persistence.mongodb.models.log import LogModel

logger = logging.getLogger(__name__)

# Sample actions for log entries
SAMPLE_ACTIONS = [
    "user.created",
    "user.updated",
    "user.deleted",
    "user.login",
    "user.logout",
    "user.password_changed",
    "session.started",
    "session.ended",
    "api.request",
    "api.error",
]


class LogSeeder:
    """Seeder for Log entity in MongoDB."""

    def __init__(self, use_test_db: bool = False):
        """Initialize the seeder.

        Args:
            use_test_db: If True, use test database instead of development.
        """
        self._use_test_db = use_test_db

    @property
    def entity_name(self) -> str:
        """Return the entity name."""
        return "log"

    @property
    def database_type(self) -> str:
        """Return database type."""
        return "mongodb"

    async def seed(self, count: int = 10, dry_run: bool = False) -> int:
        """Seed log data.

        Args:
            count: Number of logs to seed.
            dry_run: If True, preview without making changes.

        Returns:
            Number of seeded records.
        """
        if dry_run:
            logger.info(f"[DRY RUN] Would seed {count} logs")
            return count

        await mongo_db_manager.connect(use_test_db=self._use_test_db)
        try:
            # Generate sample logs
            logs_to_create = []
            now = datetime.now(timezone.utc)

            for i in range(count):
                # Generate random timestamp within the last 30 days
                random_days = random.randint(0, 30)
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                timestamp = now - timedelta(
                    days=random_days, hours=random_hours, minutes=random_minutes
                )

                action = random.choice(SAMPLE_ACTIONS)
                user_id = str(uuid4()) if random.random() > 0.2 else None

                log = LogModel(
                    action=action,
                    user_id=user_id,
                    timestamp=timestamp,
                    metadata={
                        "seeded": True,
                        "seed_index": i,
                        "source": "cli_seeder",
                    },
                )
                logs_to_create.append(log)

            # Insert all logs
            if logs_to_create:
                await LogModel.insert_many(logs_to_create)

            logger.info(f"Successfully seeded {len(logs_to_create)} logs")
            return len(logs_to_create)
        finally:
            await mongo_db_manager.close()

    async def clear(self, dry_run: bool = False) -> int:
        """Clear all log data.

        Args:
            dry_run: If True, preview without making changes.

        Returns:
            Number of cleared records.
        """
        await mongo_db_manager.connect(use_test_db=self._use_test_db)
        try:
            # Count logs first
            log_count = await LogModel.count()

            if dry_run:
                logger.info(f"[DRY RUN] Would clear {log_count} logs")
                return log_count

            if log_count == 0:
                logger.info("No logs to clear")
                return 0

            # Delete all logs
            await LogModel.delete_all()

            logger.info(f"Cleared {log_count} logs")
            return log_count
        finally:
            await mongo_db_manager.close()

    async def count(self) -> int:
        """Count existing logs.

        Returns:
            Current number of logs in the database.
        """
        await mongo_db_manager.connect(use_test_db=self._use_test_db)
        try:
            return await LogModel.count()
        finally:
            await mongo_db_manager.close()
