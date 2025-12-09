"""Integration tests for user event handlers."""

from uuid import uuid4

import pytest

from app.core.application.commands.handlers.log_handlers import CreateLogHandler
from app.core.domain.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserUpdated,
)
from app.infrastructure.event_handlers.user_event_handlers import UserEventHandler
from app.infrastructure.messaging.event_bus import InMemoryEventBus
from app.infrastructure.persistence.mongodb.repositories.log_read import (
    MongoLogReadRepository,
)
from app.infrastructure.persistence.mongodb.repositories.log_write import (
    MongoLogWriteRepository,
)

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestUserEventHandlers:
    """Integration tests for UserEventHandler with real MongoDB."""

    @pytest.fixture
    def log_write_repo(self):
        """Create log write repository."""
        return MongoLogWriteRepository()

    @pytest.fixture
    def log_read_repo(self):
        """Create log read repository."""
        return MongoLogReadRepository()

    @pytest.fixture
    def create_log_handler(self, log_write_repo):
        """Create log handler with real repository."""
        return CreateLogHandler(repository=log_write_repo)

    @pytest.fixture
    def user_event_handler(self, create_log_handler):
        """Create user event handler."""
        return UserEventHandler(create_log_handler=create_log_handler)

    @pytest.fixture
    def event_bus(self, user_event_handler):
        """Create event bus with user event handlers subscribed."""
        bus = InMemoryEventBus()
        bus.subscribe(UserCreated, user_event_handler.on_user_created)
        bus.subscribe(UserUpdated, user_event_handler.on_user_updated)
        bus.subscribe(UserDeleted, user_event_handler.on_user_deleted)
        bus.subscribe(UserDeactivated, user_event_handler.on_user_deactivated)
        bus.subscribe(UserActivated, user_event_handler.on_user_activated)
        return bus

    async def test_user_created_event_creates_log(
        self, clean_mongodb, user_event_handler, log_read_repo
    ):
        """Test that UserCreated event creates a log entry."""
        user_id = str(uuid4())
        event = UserCreated(
            user_id=user_id,
            email="created@example.com",
            username="createduser",
        )

        # Handle event
        await user_event_handler.on_user_created(event)

        # Verify log was created
        logs = await log_read_repo.list_by_user(user_id)
        assert len(logs) == 1

        log = logs[0]
        assert log.log.action.value == "user_created"
        assert log.log.user_id == user_id
        assert log.log.metadata.get("email") == "created@example.com"
        assert log.log.metadata.get("username") == "createduser"

    async def test_user_updated_event_creates_log(
        self, clean_mongodb, user_event_handler, log_read_repo
    ):
        """Test that UserUpdated event creates a log entry."""
        user_id = str(uuid4())
        changes = {"full_name": "New Name", "username": "newusername"}
        event = UserUpdated(
            user_id=user_id,
            changes=changes,
        )

        # Handle event
        await user_event_handler.on_user_updated(event)

        # Verify log was created
        logs = await log_read_repo.list_by_user(user_id)
        assert len(logs) == 1

        log = logs[0]
        assert log.log.action.value == "user_updated"
        assert log.log.user_id == user_id
        assert log.log.metadata.get("changes") == changes

    async def test_user_deleted_event_creates_log(
        self, clean_mongodb, user_event_handler, log_read_repo
    ):
        """Test that UserDeleted event creates a log entry."""
        user_id = str(uuid4())
        deleted_by = str(uuid4())
        event = UserDeleted(
            user_id=user_id,
            deleted_by=deleted_by,
        )

        # Handle event
        await user_event_handler.on_user_deleted(event)

        # Verify log was created
        logs = await log_read_repo.list_by_user(user_id)
        assert len(logs) == 1

        log = logs[0]
        assert log.log.action.value == "user_deleted"
        assert log.log.user_id == user_id
        assert log.log.metadata.get("deleted_by") == deleted_by

    async def test_user_deactivated_event_creates_log(
        self, clean_mongodb, user_event_handler, log_read_repo
    ):
        """Test that UserDeactivated event creates a log entry."""
        user_id = str(uuid4())
        reason = "User requested deactivation"
        event = UserDeactivated(
            user_id=user_id,
            reason=reason,
        )

        # Handle event
        await user_event_handler.on_user_deactivated(event)

        # Verify log was created
        logs = await log_read_repo.list_by_user(user_id)
        assert len(logs) == 1

        log = logs[0]
        assert log.log.action.value == "user_deactivated"
        assert log.log.user_id == user_id
        assert log.log.metadata.get("reason") == reason

    async def test_user_activated_event_creates_log(
        self, clean_mongodb, user_event_handler, log_read_repo
    ):
        """Test that UserActivated event creates a log entry."""
        user_id = str(uuid4())
        event = UserActivated(user_id=user_id)

        # Handle event
        await user_event_handler.on_user_activated(event)

        # Verify log was created
        logs = await log_read_repo.list_by_user(user_id)
        assert len(logs) == 1

        log = logs[0]
        assert log.log.action.value == "user_activated"
        assert log.log.user_id == user_id


class TestEventBusIntegration:
    """Integration tests for event bus with handlers and MongoDB."""

    @pytest.fixture
    def log_write_repo(self):
        """Create log write repository."""
        return MongoLogWriteRepository()

    @pytest.fixture
    def log_read_repo(self):
        """Create log read repository."""
        return MongoLogReadRepository()

    @pytest.fixture
    def create_log_handler(self, log_write_repo):
        """Create log handler with real repository."""
        return CreateLogHandler(repository=log_write_repo)

    @pytest.fixture
    def user_event_handler(self, create_log_handler):
        """Create user event handler."""
        return UserEventHandler(create_log_handler=create_log_handler)

    @pytest.fixture
    def event_bus(self, user_event_handler):
        """Create event bus with user event handlers subscribed."""
        bus = InMemoryEventBus()
        bus.subscribe(UserCreated, user_event_handler.on_user_created)
        bus.subscribe(UserUpdated, user_event_handler.on_user_updated)
        bus.subscribe(UserDeleted, user_event_handler.on_user_deleted)
        return bus

    async def test_event_bus_publishes_to_handlers(
        self, clean_mongodb, event_bus, log_read_repo
    ):
        """Test that event bus correctly publishes events to handlers."""
        user_id = str(uuid4())
        event = UserCreated(
            user_id=user_id,
            email="bus@example.com",
            username="bususer",
        )

        # Publish event through bus
        await event_bus.publish(event)

        # Verify log was created via handler
        logs = await log_read_repo.list_by_user(user_id)
        assert len(logs) == 1
        assert logs[0].log.action.value == "user_created"

    async def test_multiple_events_create_multiple_logs(
        self, clean_mongodb, event_bus, log_read_repo
    ):
        """Test that multiple events create multiple log entries."""
        user_id = str(uuid4())

        # Publish multiple events
        await event_bus.publish(
            UserCreated(
                user_id=user_id,
                email="multi@example.com",
                username="multiuser",
            )
        )
        await event_bus.publish(
            UserUpdated(
                user_id=user_id,
                changes={"full_name": "Updated Name"},
            )
        )
        await event_bus.publish(
            UserDeleted(
                user_id=user_id,
                deleted_by=None,
            )
        )

        # Verify all logs were created
        logs = await log_read_repo.list_by_user(user_id)
        assert len(logs) == 3

        actions = {log.log.action.value for log in logs}
        assert actions == {"user_created", "user_updated", "user_deleted"}
