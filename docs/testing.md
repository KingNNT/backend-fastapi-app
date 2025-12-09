# Testing Documentation

## Overview

This project implements a comprehensive testing strategy following Clean Architecture principles. Tests are organized by layer and purpose, with clear separation between unit, integration, and end-to-end tests.

## Testing Stack

- **Framework**: pytest
- **Async Support**: pytest-asyncio
- **Mocking**: unittest.mock (AsyncMock, MagicMock)
- **Coverage**: pytest-cov
- **Integration**: testcontainers (isolated database containers)
- **Test Runner**: Docker-based execution

## Test Structure

```
tests/                              # Test suite (outside app/)
├── unit/                           # Unit tests (mocked dependencies)
│   ├── domain/                     # Domain layer tests
│   │   ├── test_aggregates.py      # Aggregate tests
│   │   ├── test_entities.py        # Entity tests
│   │   └── test_value_objects.py   # Value object tests
│   └── application/                # Application layer tests
│       ├── test_command_handlers.py # Command handler tests
│       └── test_query_handlers.py   # Query handler tests
├── integration/                    # Integration tests (testcontainers)
│   ├── postgresql/                 # PostgreSQL repository tests
│   └── mongodb/                    # MongoDB repository tests
├── e2e/                            # End-to-end tests
│   └── test_user_api.py            # Full API flow tests
└── conftest.py                     # Shared test fixtures
```

## Running Tests

### Docker-First Approach

All tests run inside Docker containers:

```bash
# Run unit tests
make test

# Run tests with coverage
make test-cov

# Run integration tests (uses testcontainers)
make test-integration

# Run E2E tests (uses test databases)
make test-e2e

# Run all tests
make test-all

# Full CI pipeline
make ci
```

### Test Database Setup

```bash
# Setup test databases before first E2E run
make setup-test-db

# Reset test databases
make test-db-reset

# Access test database shells
make shell-postgres-test
make shell-mongo-test
```

## Unit Testing

### Philosophy

Unit tests focus on testing business logic in isolation:
- **Fast execution**: No database dependencies
- **Isolated**: Mock external dependencies
- **Focused**: Test one unit of functionality
- **Deterministic**: Same input always produces same output

### Testing Domain Layer

#### Value Objects

```python
# tests/unit/domain/test_value_objects.py
class TestEmail:
    def test_valid_email(self):
        email = Email("test@example.com")
        assert str(email) == "test@example.com"

    def test_invalid_email_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc_info:
            Email("invalid-email")
        assert exc_info.value.field_name == "email"

    def test_email_domain(self):
        email = Email("user@example.com")
        assert email.domain == "example.com"
```

#### Entities

```python
# tests/unit/domain/test_entities.py
class TestUser:
    def test_user_creation(self):
        user = User(
            id=UserId.generate(),
            email=Email("test@example.com"),
            username=Username("testuser"),
            password_hash="hashed",
        )
        assert user.is_active is True

    def test_user_deactivate(self):
        user = create_test_user()
        user.deactivate()
        assert user.is_active is False

    def test_user_soft_delete(self):
        user = create_test_user()
        user.soft_delete("admin")
        assert user.is_deleted is True
        assert user.deleted_by == "admin"
```

#### Aggregates

```python
# tests/unit/domain/test_aggregates.py
class TestUserAggregate:
    def test_create_raises_user_created_event(self):
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password_hash="hashed",
        )

        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserCreated)
        assert aggregate.events[0].email == "test@example.com"

    def test_update_email_raises_email_updated_event(self):
        aggregate = UserAggregate.create(
            email=Email("old@example.com"),
            username=Username("testuser"),
            password_hash="hashed",
        )
        aggregate.clear_events()

        aggregate.update_email(Email("new@example.com"))

        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserEmailUpdated)
        assert aggregate.events[0].old_email == "old@example.com"
        assert aggregate.events[0].new_email == "new@example.com"

    def test_reconstitute_does_not_raise_events(self):
        user = create_test_user()
        aggregate = UserAggregate.reconstitute(user)

        assert len(aggregate.events) == 0
```

### Testing Application Layer

#### Command Handlers

```python
# tests/unit/application/test_command_handlers.py
class TestCreateUserHandler:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def mock_domain_service(self, mock_repository):
        return UserDomainService(mock_repository)

    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock(spec=IEventBus)

    @pytest.fixture
    def mock_password_hasher(self):
        hasher = AsyncMock(spec=IPasswordHasher)
        hasher.hash.return_value = "hashed_password"
        return hasher

    @pytest.fixture
    def handler(self, mock_repository, mock_domain_service, mock_event_bus, mock_password_hasher):
        return CreateUserHandler(
            repository=mock_repository,
            domain_service=mock_domain_service,
            event_bus=mock_event_bus,
            password_hasher=mock_password_hasher,
        )

    async def test_create_user_success(self, handler, mock_repository, mock_event_bus):
        # Arrange
        mock_repository.exists_by_email.return_value = False
        mock_repository.exists_by_username.return_value = False

        command = CreateUserCommand(
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User",
        )

        # Act
        user_id = await handler.handle(command)

        # Assert
        assert user_id is not None
        mock_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called()

    async def test_create_user_duplicate_email_raises_error(self, handler, mock_repository):
        # Arrange
        mock_repository.exists_by_email.return_value = True

        command = CreateUserCommand(
            email="existing@example.com",
            username="testuser",
            password="password123",
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExists) as exc_info:
            await handler.handle(command)

        assert exc_info.value.context["field"] == "email"
```

#### Query Handlers

```python
# tests/unit/application/test_query_handlers.py
class TestGetUserByIdHandler:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def handler(self, mock_repository):
        return GetUserByIdHandler(repository=mock_repository)

    async def test_get_user_returns_read_model(self, handler, mock_repository):
        # Arrange
        expected = UserReadModel(
            id="123",
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repository.get_by_id.return_value = expected

        query = GetUserByIdQuery(user_id="123")

        # Act
        result = await handler.handle(query)

        # Assert
        assert result == expected
        mock_repository.get_by_id.assert_called_once_with("123")

    async def test_get_user_not_found_returns_none(self, handler, mock_repository):
        # Arrange
        mock_repository.get_by_id.return_value = None
        query = GetUserByIdQuery(user_id="nonexistent")

        # Act
        result = await handler.handle(query)

        # Assert
        assert result is None
```

## Integration Testing

### Using Testcontainers

Integration tests use testcontainers for isolated database instances:

```python
# tests/integration/postgresql/test_user_repository.py
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres

@pytest.fixture
async def postgres_session(postgres_container):
    engine = create_async_engine(postgres_container.get_connection_url())
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

class TestPostgresUserRepository:
    async def test_save_and_retrieve_user(self, postgres_session):
        # Arrange
        repository = PostgresUserRepository(postgres_session)
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password_hash="hashed",
        )

        # Act
        await repository.save(aggregate)
        retrieved = await repository.get_by_id(aggregate.user.id)

        # Assert
        assert retrieved is not None
        assert str(retrieved.user.email) == "test@example.com"

    async def test_exists_by_email(self, postgres_session):
        # Arrange
        repository = PostgresUserRepository(postgres_session)
        aggregate = UserAggregate.create(
            email=Email("exists@example.com"),
            username=Username("existsuser"),
            password_hash="hashed",
        )
        await repository.save(aggregate)

        # Act & Assert
        assert await repository.exists_by_email(Email("exists@example.com")) is True
        assert await repository.exists_by_email(Email("notexists@example.com")) is False
```

### MongoDB Integration Tests

```python
# tests/integration/mongodb/test_log_repository.py
from testcontainers.mongodb import MongoDbContainer

@pytest.fixture(scope="module")
def mongodb_container():
    with MongoDbContainer("mongo:7.0") as mongo:
        yield mongo

@pytest.fixture
async def mongodb_client(mongodb_container):
    client = AsyncIOMotorClient(mongodb_container.get_connection_url())
    await init_beanie(database=client.test_db, document_models=[LogModel])
    yield client
    await client.close()

class TestMongoLogRepository:
    async def test_save_and_retrieve_log(self, mongodb_client):
        repository = MongoLogRepository()
        aggregate = LogAggregate.create(
            action="USER_CREATED",
            user_id="user-123",
            metadata={"email": "test@example.com"},
        )

        await repository.save(aggregate)
        retrieved = await repository.get_by_id(aggregate.log.id)

        assert retrieved is not None
        assert retrieved.log.action == "USER_CREATED"
```

## End-to-End Testing

### E2E Test Configuration

E2E tests use separate test databases on running Docker services:

```python
# tests/e2e/conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
async def cleanup_database():
    # Clean up test data before each test
    yield
    # Clean up test data after each test
```

### E2E Tests

```python
# tests/e2e/test_user_api.py
class TestUserAPI:
    async def test_create_user(self, test_client):
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User",
        }

        # Act
        response = await test_client.post("/v1/users/", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]

    async def test_get_user_by_id(self, test_client):
        # Create user first
        create_response = await test_client.post("/v1/users/", json={...})
        user_id = create_response.json()["data"]["id"]

        # Get user
        response = await test_client.get(f"/v1/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == user_id

    async def test_get_nonexistent_user_returns_404(self, test_client):
        response = await test_client.get("/v1/users/nonexistent-id")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "USER_NOT_FOUND"

    async def test_create_duplicate_email_returns_409(self, test_client):
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123",
        }
        await test_client.post("/v1/users/", json=user_data)

        # Try to create another user with same email
        user_data["username"] = "user2"
        response = await test_client.post("/v1/users/", json=user_data)

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "USER_ALREADY_EXISTS"

    async def test_user_crud_workflow(self, test_client):
        # Create
        create_response = await test_client.post("/v1/users/", json={
            "email": "crud@example.com",
            "username": "cruduser",
            "password": "password123",
        })
        assert create_response.status_code == 201
        user_id = create_response.json()["data"]["id"]

        # Read
        get_response = await test_client.get(f"/v1/users/{user_id}")
        assert get_response.status_code == 200

        # Update
        update_response = await test_client.put(f"/v1/users/{user_id}", json={
            "full_name": "Updated Name",
        })
        assert update_response.status_code == 200

        # Delete
        delete_response = await test_client.delete(f"/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify deleted
        get_deleted_response = await test_client.get(f"/v1/users/{user_id}")
        assert get_deleted_response.status_code == 404
```

## Test Configuration

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--asyncio-mode=auto",
]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
]
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["app"]
omit = [
    "app/main.py",
    "*/migrations/*",
    "*/seeds/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

## Testing Patterns

### Arrange-Act-Assert (AAA)

```python
async def test_create_user_success(self, handler, mock_repository):
    # Arrange
    mock_repository.exists_by_email.return_value = False
    command = CreateUserCommand(email="test@example.com", ...)

    # Act
    result = await handler.handle(command)

    # Assert
    assert result is not None
    mock_repository.save.assert_called_once()
```

### Parameterized Tests

```python
@pytest.mark.parametrize("email,is_valid", [
    ("valid@example.com", True),
    ("invalid-email", False),
    ("@example.com", False),
    ("user@", False),
    ("a@b.co", True),
])
def test_email_validation(email, is_valid):
    if is_valid:
        assert Email(email).value == email
    else:
        with pytest.raises(ValidationError):
            Email(email)
```

### Test Fixtures

```python
# tests/conftest.py
@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User",
    }

@pytest.fixture
def create_test_user():
    def _create(**overrides):
        defaults = {
            "id": UserId.generate(),
            "email": Email("test@example.com"),
            "username": Username("testuser"),
            "password_hash": "hashed",
        }
        defaults.update(overrides)
        return User(**defaults)
    return _create
```

## Coverage Targets

- **Unit tests**: 90%+ coverage
- **Domain layer**: 95%+ coverage
- **Application layer**: 90%+ coverage
- **Overall**: 85%+ coverage

## Running Coverage

```bash
# Run tests with coverage
make test-cov

# Generate HTML coverage report
make shell
poetry run pytest --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

## Best Practices

### Test Design

1. **Keep tests simple**: One assertion per test when possible
2. **Use descriptive names**: Test names should explain what they test
3. **Test edge cases**: Include boundary conditions and error cases
4. **Mock external dependencies**: Keep tests isolated
5. **Use fixtures**: Reuse common test data and setup

### Test Organization

1. **Mirror source structure**: Test files match source structure
2. **Separate by type**: unit/, integration/, e2e/
3. **Use markers**: Mark slow tests, integration tests, etc.
4. **Clean test data**: Always clean up after tests

### Continuous Integration

```bash
# Run full CI pipeline locally
make ci

# This runs:
# - make build
# - make up
# - make test-cov
# - make check
```
