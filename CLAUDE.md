# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Workflow (Docker-First)

This project uses a **Docker-first development approach**. All commands run inside Docker containers using the provided Makefile.

### Quick Start
```bash
# Build and start all services
make dev

# Or step by step:
make build    # Build Docker images
make up       # Start services
make logs     # View logs
```

### Essential Commands
```bash
# Development
make dev           # Full development setup (build, up, logs)
make up            # Start services in background
make down          # Stop all services
make restart       # Restart services
make rebuild       # Rebuild and restart

# Code Quality (runs in Docker)
make format        # Format code with ruff
make lint          # Run linting
make typecheck     # Run type checking with pyright
make fix          # Format and fix all issues
make check        # Run all quality checks (format, lint, typecheck)

# Testing (runs in Docker)
make test         # Run unit tests
make test-cov     # Run tests with coverage
make test-all     # Run all tests
make ci           # Full CI pipeline

# Database Management
make db-up        # Start only MongoDB
make db-reset     # Reset MongoDB data (WARNING: deletes all data)
make shell-mongo  # Access MongoDB shell

# Utilities
make shell        # Access Python container shell
make health       # Check application health
make version      # Show application version
```

### Never Run Locally
- **DO NOT** run `poetry install` locally
- **DO NOT** run `uvicorn` or `python` commands locally
- **DO NOT** run `pytest`, `ruff`, or `pyright` commands locally
- **Always** use `make` commands which run everything in Docker containers
- The only exception is `make` itself, which orchestrates Docker containers

### Docker Services
- `python`: FastAPI application container
- `mongodb`: MongoDB database container
- Both services defined in `docker-compose.development.yaml`

## Architecture Overview

### Clean Architecture Pattern
This FastAPI application follows clean architecture principles with clear separation of concerns and modern design patterns:

- **Models** (`app/internal/models/`): MongoDB documents using Beanie ODM, inherit from BaseEntity
- **DTOs** (`app/internal/dtos/`): Data Transfer Objects for API contracts with barrel exports
- **Services** (`app/internal/services/`): Business logic layer with singleton pattern and dependency injection
- **Repositories** (`app/internal/repositories/`): Data access layer with repository pattern
- **Routers** (`app/routers/`): API layer with centralized version organization (`v1/`)
- **Dependencies** (`app/dependencies/`): Middleware and dependency injection organization

### Technology Stack
- **Framework**: FastAPI with async support and dependency injection
- **Database**: MongoDB with Motor (async driver) and Beanie (ODM)
- **Containerization**: Docker with docker-compose for development and production
- **Code Quality**: Ruff for formatting and linting, Pyright for type checking
- **Testing**: pytest with pytest-asyncio and comprehensive mocking
- **Configuration**: Pydantic Settings with environment variables and global logging

### Key Architectural Decisions

**🔄 Singleton Services Pattern**: Services use singleton pattern for efficient resource management:
- Single instance per application lifecycle
- Proper initialization with `_initialized` flag
- Dependency injection support with `get_user_service()` functions
- Memory efficient and consistent state management

**📦 Barrel Export Pattern**: All modules use `__init__.py` files for clean imports:
- Centralized exports: `from app.internal.services import UserService`
- Better module organization and discoverability
- Consistent import patterns across the application
- Easier refactoring and dependency management

**🚀 Centralized API Versioning**: V1 router architecture with prefix management:
- `app/routers/v1/__init__.py` defines `/v1` prefix once
- Individual routers don't need version prefixes
- Clean upgrade path for API evolution
- Centralized route organization

**📝 Global Logging Configuration**: Centralized logging with datetime formatting:
- `app/configs/logging.py` provides comprehensive logging config
- Global application in `main.py` using `logging.config.dictConfig()`
- Datetime formatting: `[2024-01-01 12:00:00] app.service.user - INFO - Message`
- Use `logging.getLogger(__name__)` anywhere for consistent formatting

**🔌 Dependencies Folder Structure**: Organized middleware and dependency injection:
- `app/dependencies/middleware.py` contains all middleware classes
- `app/dependencies/__init__.py` exports middleware for clean imports
- Request logging middleware with timing and emoji indicators
- Security headers middleware for production safety

**Base Entity Pattern**: All models inherit from `BaseEntity` (Beanie Document) providing:
- UUID-based IDs with automatic generation
- Audit trail fields (created_by, updated_by, deleted_by)
- Soft deletion with `deleted_at` field and `soft_delete()` method
- Timezone-aware datetime using `datetime.now(timezone.utc)`
- MongoDB indexes for performance

**MongoDB Integration**:
- Beanie ODM for async MongoDB operations
- Motor driver for high-performance async database access
- Database lifespan management in FastAPI application
- Connection pooling and automatic reconnection

**Repository Pattern**:
- Separate data access layer for MongoDB operations
- Async repository methods for CRUD operations
- Business logic separated from data access
- Easy mocking for unit tests

**Configuration Management**:
- Pydantic Settings with environment variable support
- MongoDB connection string configuration
- Singleton pattern using `@lru_cache()` decorators
- Environment-aware configuration (development/staging/production)
- Global logging configuration with datetime formatting

**Docker-First Development**:
- All development commands run in Docker containers
- MongoDB service integrated with docker-compose
- Makefile provides consistent development workflow
- No local Python environment required

### Data Flow Pattern
1. **Request** → Router (validation, serialization)
2. **Router** → Middleware (logging, security headers, timing)
3. **Router** → Dependency Injection (`get_user_service()`)
4. **Router** → Service (business logic, audit tracking, singleton instance)
5. **Service** → Repository (data access layer)
6. **Repository** → MongoDB (via Beanie ODM)
7. **Response** ← DTO (clean API contracts)

### Environment Configuration
The application uses environment-based configuration with `.env` file support:
- Development: Auto-reload, debug mode, detailed logging
- Production: Optimized settings, security headers, structured logging
- Configurable via environment variables or `.env` file

### Database Strategy
MongoDB with Beanie ODM:
- Async operations with Motor driver
- Document-based storage with flexible schema
- Repository pattern abstracts data access
- Models inherit from Beanie Document via BaseEntity
- UUID-based IDs support distributed systems
- Soft deletion preserves audit trail
- Indexes for performance optimization
- Connection management with lifespan events

### Testing Structure
- Unit tests: `app/tests/unit/` (business logic with mocked dependencies)
- E2E tests: `app/tests/e2e/` (full integration tests)
- Service layer testing with mock repositories
- pytest-asyncio for async test support
- pytest configuration in pyproject.toml
- All tests run in Docker containers via Makefile

## Important Implementation Details

### Modern Code Patterns

**Use Barrel Exports for Imports**:
```python
# ✅ Correct - Use barrel exports
from app.internal.services import UserService, get_user_service
from app.internal.dtos import UserCreate, UserResponse
from app.internal.exceptions import UserNotFound, UserAlreadyExists

# ❌ Avoid - Direct file imports
from app.internal.services.user import UserService
from app.internal.dtos.user import UserCreate
```

**Use Singleton Services with Dependency Injection**:
```python
# ✅ Correct - FastAPI dependency injection
@router.post("/")
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_data)

# ❌ Avoid - Direct service instantiation
user_service = UserService()  # Creates new instance every time
```

**Use Standard Logging Pattern**:
```python
# ✅ Correct - Standard logging with global config
import logging
logger = logging.getLogger(__name__)

logger.info("User created successfully")  # Gets datetime formatting automatically

# ❌ Avoid - Print statements or manual logging config
print("User created")  # No datetime, not structured
```

**Use Centralized API Versioning**:
```python
# ✅ Correct - V1 router handles prefix
# app/routers/v1/__init__.py
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(user.router)

# app/routers/v1/user.py
router = APIRouter(prefix="/users")  # Just the resource prefix

# ❌ Avoid - Version prefix in individual routers
router = APIRouter(prefix="/v1/users")  # Duplication and hard to change
```

### DateTime Handling
Always use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()` for timezone-aware datetime objects.

### Audit Trail
All entities automatically track:
- Who created/updated/deleted the record (`created_by`, `updated_by`, `deleted_by`)
- When these actions occurred (`created_at`, `updated_at`, `deleted_at`)
- Soft deletion preserves data for audit purposes

### Error Handling & Response Format
**Clean Architecture Pattern**: Services raise domain exceptions (never HTTPException), API layer converts to HTTP responses using class-based exception handlers and standardized APIResponse utility.

**Domain Exception Flow**:
1. Service layer raises domain exceptions (`UserNotFound`, `ValidationError`, etc.)
2. Exception handlers automatically convert to standardized HTTP responses
3. All responses follow consistent format via `APIResponse` utility

**Standardized Response Format**:
All API responses use consistent structure via `APIResponse` utility:

**Success Response**:
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { /* actual response data */ },
    "meta": { /* optional pagination/metadata */ }
}
```

**Error Response**:
```json
{
    "success": false,
    "message": "Error description",
    "error_code": "MACHINE_READABLE_CODE",
    "data": null,
    "context": { /* error-specific context */ }
}
```

**APIResponse Methods**:
- `APIResponse.success_response()` - For successful operations
- `APIResponse.error_response()` - For manual error responses
- `APIResponse.from_domain_exception()` - Auto-converts domain exceptions

### API Response Patterns
- Create: 201 Created with success response format
- Read: 200 OK with success response format
- Update: 200 OK with success response format
- Delete: 204 No Content with success response format
- Errors: Appropriate HTTP status with error response format

### MongoDB Specific
- All models inherit from Beanie's `Document` class via `BaseEntity`
- Use async/await for all database operations
- Repository pattern isolates MongoDB operations
- Connection managed through FastAPI lifespan events

### Development Workflow
- **Always run commands through Makefile** (Docker-first approach)
- Use `make format`, `make lint`, and `make typecheck` before committing
- Run `make test` to ensure all tests pass
- Use `make ci` for full CI pipeline simulation
- Access services via `make shell` or `make shell-mongo`

## API Endpoints

### System Endpoints
- `GET /health-check` - Application health status
- `GET /version` - Application version info

### User API (v1)
- `POST /v1/users/` - Create new user
- `GET /v1/users/` - List users (with pagination)
- `GET /v1/users/{id}` - Get user by ID
- `PUT /v1/users/{id}` - Update user
- `DELETE /v1/users/{id}` - Soft delete user
- `GET /v1/users/by-email/{email}` - Get user by email
- `GET /v1/users/by-username/{username}` - Get user by username

### API Documentation
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Environment Variables

### Application Settings
- `APP_NAME`: Application name
- `APP_VERSION`: Application version
- `ENVIRONMENT`: Environment (development/staging/production)
- `DEBUG`: Debug mode flag
- `LOG_LEVEL`: Logging level

### MongoDB Settings
- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name
- `MONGODB_TEST_DB_NAME`: Test database name

### Server Settings
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8080)
- `RELOAD`: Auto-reload on changes (development only)

## File Structure
```
app/
├── configs/          # Configuration modules
│   ├── __init__.py  # ✨ Barrel exports for all configurations
│   ├── app.py       # Main app configuration
│   ├── database.py  # MongoDB configuration
│   ├── logging.py   # Global logging configuration with datetime
│   └── version.py   # Version management
├── dependencies/     # 🆕 Dependency injection and middleware
│   ├── __init__.py      # Middleware exports for dependency injection
│   └── middleware.py    # Request logging, security headers, timing
├── internal/         # Domain/business logic layer
│   ├── __init__.py  # Internal module organization
│   ├── dtos/            # Data Transfer Objects
│   │   ├── __init__.py      # ✨ All DTOs exported via barrel pattern
│   │   ├── system.py        # System-related DTOs
│   │   └── user.py          # User-related DTOs and validation
│   ├── exceptions/      # Domain exceptions organized by type
│   │   ├── __init__.py          # ✨ All exceptions with barrel exports
│   │   ├── base.py              # Base exception classes
│   │   ├── handlers.py          # Exception to HTTP response handlers
│   │   ├── infrastructure.py    # Infrastructure exceptions
│   │   ├── user.py              # User domain exceptions
│   │   └── validation.py        # Validation & business rule exceptions
│   ├── models/          # MongoDB models (Beanie)
│   │   ├── __init__.py      # ✨ Model exports with barrel pattern
│   │   ├── base.py          # BaseEntity with audit trail and soft delete
│   │   └── user.py          # User model with indexes and validation
│   ├── repositories/    # Data access layer
│   │   ├── __init__.py      # ✨ Repository exports
│   │   └── user.py          # User repository with async MongoDB operations
│   └── services/        # Business logic with singleton pattern
│       ├── __init__.py      # ✨ Service exports including dependency functions
│       ├── system.py        # System service for health checks
│       └── user.py          # 🔄 Singleton UserService with DI support
├── routers/          # API route handlers
│   ├── __init__.py  # Router organization
│   ├── system.py    # System endpoints
│   └── v1/              # 🚀 Version 1 API with centralized management
│       ├── __init__.py      # V1 router with /v1 prefix centralization
│       └── user.py          # User endpoints
├── utils/            # Utility functions and helpers
│   ├── __init__.py      # Utility exports
│   └── response.py      # Standardized API response utilities
├── tests/            # Test suite
│   ├── __init__.py  # Test configuration
│   ├── conftest.py  # Shared test fixtures and configuration
│   ├── unit/            # Unit tests with comprehensive mocking
│   └── e2e/             # End-to-end integration tests
└── main.py           # 🎯 Application entry point with global configuration
```

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.


      IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task.
