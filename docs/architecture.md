# Architecture Documentation

## Overview

This FastAPI application follows clean architecture principles with clear separation of concerns, ensuring maintainability, testability, and scalability. The architecture incorporates modern design patterns including singleton services, barrel exports, and comprehensive dependency injection.

## Clean Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                         │
│         (FastAPI Routers + Middleware)              │
│  • V1 Router Architecture with centralized routing  │
│  • Request/Response middleware with logging         │
│  • Security headers and timing middleware          │
├─────────────────────────────────────────────────────┤
│                Business Logic                       │
│              (Singleton Services)                   │
│  • Singleton pattern with dependency injection     │
│  • Domain exception handling                       │
│  • Business rule validation                        │
├─────────────────────────────────────────────────────┤
│                Data Access                          │
│            (Repository Pattern)                     │
│  • Abstract data access layer                      │
│  • MongoDB operations encapsulation               │
│  • Query optimization and caching                 │
├─────────────────────────────────────────────────────┤
│                   Database                          │
│         (MongoDB + Beanie ODM + Motor)             │
│  • Async operations with connection pooling       │
│  • Document-based storage with schema validation  │
│  • Audit trail and soft deletion support         │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
app/
├── configs/           # Configuration modules
│   ├── __init__.py   # ✨ Barrel exports for all configurations
│   ├── app.py        # Main app configuration with Pydantic Settings
│   ├── database.py   # MongoDB connection and Beanie initialization
│   ├── logging.py    # Global logging configuration with datetime
│   └── version.py    # Version management and app metadata
│
├── dependencies/      # 🆕 Dependency injection and middleware
│   ├── __init__.py   # Middleware exports for dependency injection
│   └── middleware.py # Request logging, security headers, timing
│
├── internal/          # Domain/business logic layer
│   ├── __init__.py   # Internal module organization
│   ├── dtos/         # Data Transfer Objects
│   │   ├── __init__.py   # ✨ All DTOs exported via barrel pattern
│   │   ├── system.py     # System-related DTOs
│   │   └── user.py       # User-related DTOs and validation
│   ├── exceptions/   # Domain exception hierarchy
│   │   ├── __init__.py       # ✨ All exceptions with barrel exports
│   │   ├── base.py           # Base exception classes
│   │   ├── handlers.py       # Exception to HTTP response handlers
│   │   ├── infrastructure.py # Infrastructure-related exceptions
│   │   ├── user.py          # User domain exceptions
│   │   └── validation.py    # Validation and business rule exceptions
│   ├── models/       # MongoDB models with Beanie
│   │   ├── __init__.py   # ✨ Model exports with barrel pattern
│   │   ├── base.py       # BaseEntity with audit trail and soft delete
│   │   └── user.py       # User model with indexes and validation
│   ├── repositories/ # Data access layer
│   │   ├── __init__.py   # ✨ Repository exports
│   │   └── user.py       # User repository with async MongoDB operations
│   └── services/     # Business logic with singleton pattern
│       ├── __init__.py   # ✨ Service exports including dependency functions
│       ├── system.py     # System service for health checks
│       └── user.py       # 🔄 Singleton UserService with DI support
│
├── routers/          # API endpoints with version organization
│   ├── __init__.py   # Router organization
│   ├── system.py     # System endpoints (health, version)
│   └── v1/           # 🚀 Version 1 API with centralized management
│       ├── __init__.py   # V1 router with /v1 prefix centralization
│       └── user.py       # User CRUD endpoints
│
├── utils/            # Utility functions and helpers
│   ├── __init__.py   # Utility exports
│   └── response.py   # Standardized API response utilities
│
├── tests/            # Comprehensive test suite
│   ├── __init__.py   # Test configuration
│   ├── conftest.py   # Shared test fixtures and configuration
│   ├── unit/         # Unit tests with comprehensive mocking
│   └── e2e/          # End-to-end integration tests
│
└── main.py           # 🎯 Application entry point with global configuration
```

## Key Architectural Features

### 🔄 Singleton Pattern for Services

Services use the singleton pattern to ensure single instance throughout the application lifecycle:

```python
class UserService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.repository = UserRepository()
            UserService._initialized = True

# Dependency injection support
def get_user_service() -> UserService:
    return UserService()
```

### 📦 Barrel Export Pattern

All modules use `__init__.py` files for clean imports and better organization:

```python
# app/internal/services/__init__.py
from .system import SystemService
from .user import UserService, get_user_service

__all__ = ["SystemService", "UserService", "get_user_service"]

# Usage in other files
from app.internal.services import UserService, get_user_service
```

### 🚀 Centralized API Versioning

V1 router centralizes prefix management:

```python
# app/routers/v1/__init__.py
from fastapi import APIRouter
from app.routers.v1 import user

v1_router = APIRouter(prefix="/v1")  # Centralized prefix
v1_router.include_router(user.router)

# app/main.py
app.include_router(v1_router)  # No prefix needed here
```

### 📝 Global Logging Configuration

Centralized logging with datetime formatting:

```python
# app/configs/logging.py
def get_log_config(log_level: str = "INFO") -> dict[str, Any]:
    return {
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        }
        # ... comprehensive logging configuration
    }

# Usage anywhere in the application
import logging
logger = logging.getLogger(__name__)  # Automatically gets datetime formatting
```

### 🏗️ Repository Pattern

Clean separation of data access logic:

```python
class UserRepository:
    async def create(self, user: User) -> User:
        return await user.save()

    async def get_by_id(self, user_id: PydanticObjectId) -> User | None:
        return await User.get(user_id)

    async def email_exists(self, email: str, exclude_user_id: PydanticObjectId | None = None) -> bool:
        # Implementation with proper query optimization
```

## Data Flow Architecture

### Request Flow

```
1. HTTP Request → FastAPI Router
2. Router → Middleware (logging, security headers)
3. Router → Dependency Injection (get_user_service)
4. Router → Service Method (business logic)
5. Service → Repository (data access)
6. Repository → MongoDB (via Beanie ODM)
7. Response ← Standardized APIResponse format
```

### Example Request Flow

```python
# 1. Router receives request
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)  # 2. DI
) -> JSONResponse:
    user = await user_service.create_user(user_data)  # 3. Service
    return APIResponse.success_response(data=user)    # 4. Response

# 2. Service handles business logic
async def create_user(self, user_data: UserCreate) -> UserResponse:
    # Business validation
    if await self.repository.email_exists(user_data.email):
        raise UserAlreadyExists("email", user_data.email)

    # 3. Repository handles data access
    created_user = await self.repository.create(user)
    return UserResponse(**created_user.model_dump())
```

## Design Patterns Used

### 1. Singleton Pattern
- **Services**: Ensure single instance per application lifecycle
- **Configuration**: Cached configuration objects with `@lru_cache()`

### 2. Repository Pattern
- **Data Access**: Abstract database operations from business logic
- **Testing**: Easy mocking of data layer

### 3. Dependency Injection
- **FastAPI Native**: Using `Depends()` for clean dependency management
- **Service Layer**: Singleton services with injection support

### 4. Factory Pattern
- **Exception Handlers**: Creating appropriate HTTP responses from domain exceptions
- **DTOs**: Converting between domain models and API contracts

### 5. Strategy Pattern
- **Logging**: Different formatters for different log types
- **Configuration**: Environment-specific configurations

## Database Design

### BaseEntity Pattern

All models inherit from `BaseEntity` providing:

```python
class BaseEntity(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: UUID | None = None
    updated_by: UUID | None = None
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None

    def soft_delete(self, deleted_by: UUID | None = None):
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by
```

### Audit Trail Features

- **Creation Tracking**: Who and when created
- **Modification Tracking**: Who and when last modified
- **Soft Deletion**: Preserves data for audit purposes
- **Timezone Awareness**: UTC timestamps for global applications

## Error Handling Architecture

### Domain Exception Hierarchy

```python
# Base exceptions
class DomainException(Exception): pass
class ApplicationException(DomainException): pass
class InfrastructureException(DomainException): pass

# Specific domain exceptions
class UserException(DomainException): pass
class UserNotFound(UserException): pass
class UserAlreadyExists(UserException): pass
```

### Exception Flow

1. **Services**: Raise domain exceptions (never HTTP exceptions)
2. **Handlers**: Convert domain exceptions to HTTP responses
3. **API Layer**: Returns standardized error format

## Environment Configuration

### Pydantic Settings Pattern

```python
class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # Application settings with defaults
    name: str = Field(default="backend-fastapi-app")
    environment: Literal["development", "staging", "production"] = "development"

    # Database settings
    mongodb_url: str = Field(description="MongoDB connection string")
```

## Testing Architecture

### Unit Tests with Mocking

```python
class TestUserServiceBusiness:
    @pytest.fixture
    def user_service(self):
        service = UserService()
        service.repository = AsyncMock()  # Mock repository
        return service

    async def test_create_user_success(self, user_service, sample_user_create):
        # Arrange
        user_service.repository.email_exists.return_value = False

        # Act
        result = await user_service.create_user(sample_user_create)

        # Assert
        assert isinstance(result, UserResponse)
```

### Integration Tests

- **E2E Tests**: Full application stack testing
- **Database Tests**: Real MongoDB integration
- **API Tests**: HTTP endpoint testing

## Performance Considerations

### Async Operations

- **Full Async Stack**: FastAPI + Motor + Beanie
- **Connection Pooling**: MongoDB connection management
- **Non-blocking I/O**: Efficient resource utilization

### Caching Strategy

- **Configuration Caching**: `@lru_cache()` for settings
- **Service Singletons**: Reduce object creation overhead
- **Query Optimization**: Repository pattern enables query caching

### Monitoring and Observability

- **Request Logging**: Detailed request/response tracking
- **Performance Metrics**: Response time middleware
- **Health Checks**: Application and database monitoring

## Security Architecture

### Authentication & Authorization (Ready for Implementation)

- **JWT Token Support**: Ready for authentication implementation
- **Role-based Access**: Prepared user model structure
- **API Key Support**: Configurable authentication strategies

### Data Protection

- **Input Validation**: Pydantic models prevent injection
- **SQL Injection Prevention**: NoSQL with ODM protection
- **UUID-based IDs**: Prevent enumeration attacks

### Security Headers

Automatic security headers via middleware:

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
```

## Deployment Architecture

### Docker-First Approach

- **Development**: Docker Compose with hot reload
- **Production**: Multi-stage Docker builds
- **Orchestration**: Kubernetes-ready with health checks

### Environment Management

- **Configuration**: Environment-specific settings
- **Secrets**: External secret management support
- **Scaling**: Horizontal scaling with load balancers

## Future Architecture Considerations

### Planned Enhancements

- **Event Sourcing**: For complex domain events
- **CQRS**: Separate read/write models for complex queries
- **Microservices**: Service decomposition guidelines
- **API Gateway**: External API management
- **Message Queues**: Async task processing

This architecture provides a solid foundation for building scalable, maintainable FastAPI applications with modern Python practices and clean architecture principles.
