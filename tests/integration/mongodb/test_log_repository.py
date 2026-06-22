"""Integration tests for MongoDB log repository."""

from datetime import datetime, timedelta, timezone

import pytest

from app.audit.domain.log.aggregate import LogAggregate
from app.audit.domain.log.value_objects import Action
from app.audit.infrastructure.persistence.mongodb.repositories.log_read import (
    MongoLogReadModelRepository,
    MongoLogReadRepository,
)
from app.audit.infrastructure.persistence.mongodb.repositories.log_write import (
    MongoLogWriteRepository,
)

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestMongoLogWriteRepository:
    """Integration tests for MongoLogWriteRepository."""

    async def test_save_and_retrieve_log(self, clean_mongodb):
        """Test creating a log and retrieving it by ID."""
        write_repo = MongoLogWriteRepository()
        read_repo = MongoLogReadRepository()

        # Create log aggregate
        aggregate = LogAggregate.create(
            action=Action.user_created(),
            user_id="user-123",
            metadata={"email": "test@example.com"},
        )

        # Save log
        await write_repo.save(aggregate)

        # Aggregate should have ID set after save
        assert aggregate.id is not None
        assert aggregate.id_str is not None

        # Retrieve log
        retrieved = await read_repo.get_by_id(aggregate.id)

        assert retrieved is not None
        assert retrieved.log.action.value == "user_created"
        assert retrieved.log.user_id == "user-123"
        assert retrieved.log.metadata.get("email") == "test@example.com"


class TestMongoLogReadRepository:
    """Integration tests for MongoLogReadRepository."""

    async def test_list_logs_by_user(self, clean_mongodb):
        """Test listing logs by user ID."""
        write_repo = MongoLogWriteRepository()
        read_repo = MongoLogReadRepository()

        # Create logs for different users
        for i in range(3):
            aggregate = LogAggregate.create(
                action=Action.user_updated(),
                user_id="user-A",
            )
            await write_repo.save(aggregate)

        for i in range(2):
            aggregate = LogAggregate.create(
                action=Action.user_updated(),
                user_id="user-B",
            )
            await write_repo.save(aggregate)

        # List logs for user-A
        logs_a = await read_repo.list_by_user("user-A")
        assert len(logs_a) == 3

        # List logs for user-B
        logs_b = await read_repo.list_by_user("user-B")
        assert len(logs_b) == 2

        # List logs for non-existent user
        logs_c = await read_repo.list_by_user("user-C")
        assert len(logs_c) == 0

    async def test_list_logs_by_action(self, clean_mongodb):
        """Test listing logs by action type."""
        write_repo = MongoLogWriteRepository()
        read_repo = MongoLogReadRepository()

        # Create logs with different actions
        for _ in range(3):
            aggregate = LogAggregate.create(
                action=Action.user_created(),
                user_id="user-1",
            )
            await write_repo.save(aggregate)

        for _ in range(2):
            aggregate = LogAggregate.create(
                action=Action.user_deleted(),
                user_id="user-1",
            )
            await write_repo.save(aggregate)

        # List by action
        created_logs = await read_repo.list_by_action(Action.user_created())
        assert len(created_logs) == 3

        deleted_logs = await read_repo.list_by_action(Action.user_deleted())
        assert len(deleted_logs) == 2

    async def test_list_logs_by_date_range(self, clean_mongodb):
        """Test listing logs within a date range."""
        write_repo = MongoLogWriteRepository()
        read_repo = MongoLogReadRepository()

        now = datetime.now(timezone.utc)

        # Create logs
        for _ in range(5):
            aggregate = LogAggregate.create(
                action=Action.user_updated(),
                user_id="user-1",
            )
            await write_repo.save(aggregate)

        # Query with date range that includes all logs
        start = now - timedelta(minutes=1)
        end = now + timedelta(minutes=1)
        logs = await read_repo.list_by_date_range(start, end)
        assert len(logs) == 5

        # Query with future date range
        future_start = now + timedelta(days=1)
        future_end = now + timedelta(days=2)
        logs = await read_repo.list_by_date_range(future_start, future_end)
        assert len(logs) == 0

    async def test_list_logs_pagination(self, clean_mongodb):
        """Test listing logs with pagination."""
        write_repo = MongoLogWriteRepository()
        read_repo = MongoLogReadRepository()

        # Create multiple logs
        for i in range(5):
            aggregate = LogAggregate.create(
                action=Action.custom(f"action_{i}"),
                user_id="user-1",
            )
            await write_repo.save(aggregate)

        # Test pagination
        page1 = await read_repo.list_all(skip=0, limit=2)
        page2 = await read_repo.list_all(skip=2, limit=2)
        page3 = await read_repo.list_all(skip=4, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_count_logs(self, clean_mongodb):
        """Test counting logs."""
        write_repo = MongoLogWriteRepository()
        read_repo = MongoLogReadRepository()

        # Initially zero
        assert await read_repo.count() == 0

        # Create logs
        for _ in range(3):
            aggregate = LogAggregate.create(
                action=Action.user_created(),
                user_id="user-1",
            )
            await write_repo.save(aggregate)

        # Count should be 3
        assert await read_repo.count() == 3

    async def test_count_logs_by_user(self, clean_mongodb):
        """Test counting logs for a specific user."""
        write_repo = MongoLogWriteRepository()
        read_repo = MongoLogReadRepository()

        # Create logs for different users
        for _ in range(3):
            aggregate = LogAggregate.create(
                action=Action.user_created(),
                user_id="user-A",
            )
            await write_repo.save(aggregate)

        for _ in range(2):
            aggregate = LogAggregate.create(
                action=Action.user_created(),
                user_id="user-B",
            )
            await write_repo.save(aggregate)

        # Count by user
        assert await read_repo.count_by_user("user-A") == 3
        assert await read_repo.count_by_user("user-B") == 2
        assert await read_repo.count_by_user("user-C") == 0


class TestMongoLogReadModelRepository:
    """Integration tests for MongoLogReadModelRepository."""

    async def test_get_by_id_returns_read_model(self, clean_mongodb):
        """Test getting log returns LogReadModel."""
        write_repo = MongoLogWriteRepository()
        read_model_repo = MongoLogReadModelRepository()

        aggregate = LogAggregate.create(
            action=Action.user_created(),
            user_id="user-123",
            metadata={"email": "test@example.com"},
        )
        await write_repo.save(aggregate)

        # Get read model
        read_model = await read_model_repo.get_by_id(aggregate.id_str)

        assert read_model is not None
        assert read_model.id == aggregate.id_str
        assert read_model.action == "user_created"
        assert read_model.user_id == "user-123"
        assert read_model.metadata.get("email") == "test@example.com"
        assert read_model.timestamp is not None

    async def test_get_by_invalid_id_returns_none(self, clean_mongodb):
        """Test getting log with invalid ID returns None."""
        read_model_repo = MongoLogReadModelRepository()

        result = await read_model_repo.get_by_id("invalid-object-id")
        assert result is None

    async def test_list_by_user_returns_read_models(self, clean_mongodb):
        """Test listing logs by user returns LogReadModel list."""
        write_repo = MongoLogWriteRepository()
        read_model_repo = MongoLogReadModelRepository()

        # Create logs
        for i in range(3):
            aggregate = LogAggregate.create(
                action=Action.user_updated(),
                user_id="user-X",
                metadata={"index": i},
            )
            await write_repo.save(aggregate)

        # List by user
        logs = await read_model_repo.list_by_user("user-X")

        assert len(logs) == 3
        for log in logs:
            assert log.user_id == "user-X"
            assert log.action == "user_updated"

    async def test_list_by_action_returns_read_models(self, clean_mongodb):
        """Test listing logs by action returns LogReadModel list."""
        write_repo = MongoLogWriteRepository()
        read_model_repo = MongoLogReadModelRepository()

        # Create logs
        for _ in range(2):
            aggregate = LogAggregate.create(
                action=Action.user_deleted(),
                user_id="user-1",
            )
            await write_repo.save(aggregate)

        # List by action
        logs = await read_model_repo.list_by_action("user_deleted")

        assert len(logs) == 2
        for log in logs:
            assert log.action == "user_deleted"
