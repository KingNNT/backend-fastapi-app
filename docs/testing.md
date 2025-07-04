# Testing Documentation

## Overview

This project implements a comprehensive testing strategy using pytest with async support, focusing on unit tests for business logic and integration tests for full application workflows.

## Testing Stack

- **Framework**: pytest
- **Async Support**: pytest-asyncio
- **Mocking**: unittest.mock (AsyncMock, MagicMock)
- **Coverage**: pytest-cov
- **Test Runner**: Docker-based execution

## Test Structure

```
app/tests/
├── unit/                           # Unit tests
│   ├── test_user_models.py        # DTO validation tests
│   └── test_user_service_simple.py # Service logic tests
├── integration/                    # Integration tests (future)
│   └── test_user_endpoints.py     # End-to-end API tests
├── e2e/                           # End-to-end tests (future)
│   └── test_user_workflows.py     # Complete user workflows
└── conftest.py                    # Test configuration
```

## Running Tests

### Docker-First Approach

All tests run inside Docker containers:

```bash
# Run all unit tests
make test

# Run tests with coverage
make test-cov

# Run all tests (unit + integration)
make test-all

# Run tests in watch mode
make test-watch

# Run integration tests only
make test-integration

# Full CI pipeline
make ci
```

### Direct pytest Commands

Access container shell first:

```bash
# Access Python container
make shell

# Then run pytest commands
poetry run pytest app/tests/unit/ -v
poetry run pytest app/tests/unit/test_user_models.py -v
poetry run pytest -k "test_user" -v
poetry run pytest --cov=app --cov-report=html
```

## Unit Testing

### Philosophy

Unit tests focus on testing business logic in isolation:
- **Fast execution**: No database dependencies
- **Isolated**: Mock external dependencies
- **Focused**: Test one unit of functionality
- **Deterministic**: Same input always produces same output

### Service Layer Testing

#### Mock Strategy

```python
# app/tests/unit/test_user_service_simple.py
class TestUserServiceBusiness:
    @pytest.fixture
    def user_service(self):
        """Create UserService with mocked repository."""
        service = UserService()
        service.repository = AsyncMock()
        return service

    @pytest.fixture
    def sample_user_create(self):
        """Sample UserCreate data."""
        return UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
            is_active=True
        )
```

#### Testing Business Logic

```python
async def test_create_user_success(self, user_service, sample_user_create, mock_user):
    """Test successful user creation."""
    # Arrange
    user_service.repository.email_exists.return_value = False
    user_service.repository.username_exists.return_value = False
    user_service.repository.create.return_value = mock_user

    # Act
    result = await user_service.create_user(sample_user_create)

    # Assert
    assert isinstance(result, UserResponse)
    assert result.email == sample_user_create.email
    user_service.repository.create.assert_called_once()
```

#### Testing Error Conditions

```python
async def test_create_user_email_exists(self, user_service, sample_user_create):
    """Test user creation fails when email already exists."""
    # Arrange
    user_service.repository.email_exists.return_value = True

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_user(sample_user_create)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in str(exc_info.value.detail)
```

### DTO Testing

#### Validation Testing

```python
# app/tests/unit/test_user_models.py
class TestUserDTOs:
    def test_user_create_valid(self):
        """Test valid UserCreate DTO."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123",
            "is_active": True
        }

        user_create = UserCreate(**user_data)

        assert user_create.email == "test@example.com"
        assert user_create.username == "testuser"
        assert user_create.is_active is True
```

#### Error Validation Testing

```python
def test_user_create_invalid_email(self):
    """Test UserCreate with invalid email."""
    user_data = {
        "email": "invalid-email",
        "username": "testuser",
        "password": "password123"
    }

    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**user_data)

    assert "value is not a valid email address" in str(exc_info.value)
```

### Mock User Implementation

```python
class MockUser:
    """Mock User model for testing without database."""

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', uuid4())
        self.email = kwargs.get('email', '')
        self.username = kwargs.get('username', '')
        self.full_name = kwargs.get('full_name')
        self.is_active = kwargs.get('is_active', True)
        self.password_hash = kwargs.get('password_hash', '')
        self.created_at = kwargs.get('created_at', datetime.now(timezone.utc))
        self.updated_at = kwargs.get('updated_at', datetime.now(timezone.utc))

    def model_dump(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
```

## Integration Testing

### Database Integration

```python
# Future implementation
@pytest.fixture
async def test_database():
    """Set up test database."""
    await init_database(test=True)
    yield
    await cleanup_test_database()

async def test_create_user_integration(test_client, test_database):
    """Test user creation with real database."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }

    response = await test_client.post("/v1/users/", json=user_data)

    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### API Integration

```python
# Future implementation
@pytest.fixture
async def test_client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

async def test_user_crud_workflow(test_client, test_database):
    """Test complete user CRUD workflow."""
    # Create user
    create_response = await test_client.post("/v1/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Get user
    get_response = await test_client.get(f"/v1/users/{user_id}")
    assert get_response.status_code == 200

    # Update user
    update_response = await test_client.put(f"/v1/users/{user_id}", json=update_data)
    assert update_response.status_code == 200

    # Delete user
    delete_response = await test_client.delete(f"/v1/users/{user_id}")
    assert delete_response.status_code == 204
```

## Test Configuration

### pytest Configuration

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["app/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--strict-config",
    "--asyncio-mode=auto",
]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]
```

### Test Environment

```python
# app/tests/conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_user_repository():
    """Mock user repository for testing."""
    return AsyncMock()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "password123",
        "is_active": True
    }
```

## Testing Patterns

### Arrange-Act-Assert (AAA)

```python
async def test_user_creation():
    # Arrange
    user_data = UserCreate(email="test@example.com", ...)
    service.repository.email_exists.return_value = False

    # Act
    result = await service.create_user(user_data)

    # Assert
    assert isinstance(result, UserResponse)
    assert result.email == user_data.email
```

### Given-When-Then

```python
async def test_user_creation_with_duplicate_email():
    # Given
    user_data = UserCreate(email="existing@example.com", ...)
    service.repository.email_exists.return_value = True

    # When
    with pytest.raises(HTTPException) as exc_info:
        await service.create_user(user_data)

    # Then
    assert exc_info.value.status_code == 400
    assert "Email already registered" in str(exc_info.value.detail)
```

### Parameterized Tests

```python
@pytest.mark.parametrize("email,expected_valid", [
    ("valid@example.com", True),
    ("invalid-email", False),
    ("@example.com", False),
    ("user@", False),
])
def test_email_validation(email, expected_valid):
    """Test email validation with various inputs."""
    if expected_valid:
        user = UserCreate(email=email, username="test", password="password123")
        assert user.email == email
    else:
        with pytest.raises(ValidationError):
            UserCreate(email=email, username="test", password="password123")
```

## Test Coverage

### Coverage Configuration

```ini
# pyproject.toml
[tool.coverage.run]
source = ["app"]
omit = [
    "app/tests/*",
    "app/main.py",
    "*/venv/*",
    "*/virtualenv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### Running Coverage

```bash
# Run tests with coverage
make test-cov

# Generate HTML coverage report
make shell
poetry run pytest --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Coverage Targets

- **Unit tests**: 90%+ coverage
- **Business logic**: 95%+ coverage
- **DTOs**: 100% coverage
- **Overall**: 85%+ coverage

## Test Data Management

### Test Fixtures

```python
@pytest.fixture
def user_create_data():
    """User creation data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "password123",
        "is_active": True
    }

@pytest.fixture
def mock_user(user_create_data):
    """Mock user instance."""
    return MockUser(**user_create_data)
```

### Factory Pattern

```python
class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create_user_data(**overrides):
        """Create user data with optional overrides."""
        default_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "password123",
            "is_active": True
        }
        return {**default_data, **overrides}

    @staticmethod
    def create_mock_user(**overrides):
        """Create mock user instance."""
        data = UserFactory.create_user_data(**overrides)
        return MockUser(**data)
```

## Performance Testing

### Test Execution Time

```python
import time
import pytest

@pytest.mark.slow
async def test_bulk_user_creation():
    """Test creating multiple users (performance test)."""
    start_time = time.time()

    # Create 1000 users
    tasks = [create_user(f"user{i}@example.com") for i in range(1000)]
    await asyncio.gather(*tasks)

    execution_time = time.time() - start_time
    assert execution_time < 5.0  # Should complete in under 5 seconds
```

### Memory Usage

```python
import psutil
import pytest

def test_memory_usage():
    """Test memory usage during operations."""
    process = psutil.Process()
    initial_memory = process.memory_info().rss

    # Perform memory-intensive operation
    large_data = create_large_dataset()

    peak_memory = process.memory_info().rss
    memory_increase = peak_memory - initial_memory

    # Assert memory increase is reasonable
    assert memory_increase < 100 * 1024 * 1024  # Less than 100MB
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run tests
        run: |
          make ci

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Local CI Simulation

```bash
# Run full CI pipeline locally
make ci

# This runs:
# - make build
# - make up
# - make test-cov
# - make check
```

## Debugging Tests

### Test Debugging

```python
# Add debugging to tests
import logging

logging.basicConfig(level=logging.DEBUG)

async def test_with_debug():
    """Test with debug logging."""
    logger = logging.getLogger(__name__)
    logger.debug("Starting test...")

    # Test code here

    logger.debug("Test completed")
```

### Running Single Tests

```bash
# Run specific test
make shell
poetry run pytest app/tests/unit/test_user_models.py::TestUserDTOs::test_user_create_valid -v

# Run with debug output
poetry run pytest app/tests/unit/test_user_models.py -v -s

# Run with pdb debugger
poetry run pytest app/tests/unit/test_user_models.py --pdb
```

## Best Practices

### Test Design

1. **Keep tests simple**: One assertion per test when possible
2. **Use descriptive names**: Test names should explain what they test
3. **Test edge cases**: Include boundary conditions and error cases
4. **Mock external dependencies**: Keep tests isolated
5. **Use fixtures**: Reuse common test data and setup

### Test Organization

1. **Group related tests**: Use classes to group related functionality
2. **Separate unit and integration**: Different test directories
3. **Use markers**: Mark slow tests, integration tests, etc.
4. **Clean test data**: Always clean up after tests

### Test Maintenance

1. **Update tests with code**: Keep tests in sync with implementation
2. **Remove obsolete tests**: Delete tests for removed functionality
3. **Refactor test code**: Apply same quality standards as production code
4. **Document complex tests**: Explain why, not just what

## Common Testing Patterns

### Testing Async Functions

```python
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

### Testing Exceptions

```python
async def test_exception_handling():
    """Test exception is raised correctly."""
    with pytest.raises(ValueError, match="Invalid input"):
        await function_that_raises_exception()
```

### Testing with Mock Data

```python
@patch('app.services.user.User')
async def test_with_mock_model(mock_user_class):
    """Test with mocked model."""
    mock_user_class.return_value = mock_user_instance
    result = await service.create_user(user_data)
    assert result is not None
```

### Testing Database Operations

```python
async def test_database_operation():
    """Test database operation with transaction."""
    async with database.transaction():
        user = await create_user(user_data)
        assert user.id is not None

        # Transaction will rollback after test
```

## Future Enhancements

### Planned Testing Features

1. **Integration tests**: Full API testing with test database
2. **End-to-end tests**: Complete user workflows
3. **Performance tests**: Load testing and benchmarking
4. **Contract tests**: API contract validation
5. **Mutation testing**: Test quality validation

### Testing Tools

1. **Testcontainers**: Docker containers for integration tests
2. **Factory Boy**: Advanced test data generation
3. **Faker**: Realistic test data generation
4. **Hypothesis**: Property-based testing
5. **pytest-benchmark**: Performance benchmarking
