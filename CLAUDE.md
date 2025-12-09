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
make start         # Start all services (alias for up)
make stop          # Stop all services (alias for down)
make up            # Start services in background
make down          # Stop all services
make restart       # Restart services
make rebuild       # Rebuild and restart

# Code Quality (runs in Docker)
make format        # Format code with ruff
make lint          # Run linting
make typecheck     # Run type checking with pyright
make fix           # Format and fix all issues
make check         # Run all quality checks (format, lint, typecheck)

# Testing (runs in Docker)
make test          # Run unit tests
make test-cov      # Run tests with coverage
make test-integration  # Run integration tests (uses testcontainers)
make test-e2e      # Run E2E tests (uses test databases)
make test-all      # Run all tests
make ci            # Full CI pipeline

# Test Database Management
make setup-test-db    # Setup test databases (start services + create test DBs)
make test-db-create   # Create test databases
make test-db-reset    # Reset test databases (drops and recreates)
make test-db-clean    # Clean test database data (keeps structure)
make shell-postgres-test  # Access PostgreSQL test database shell
make shell-mongo-test     # Access MongoDB test database shell

# Database Management (Both PostgreSQL and MongoDB)
make db-up         # Start both databases
make db-down       # Stop both databases
make db-reset      # Reset all database data (WARNING: deletes all data)

# MongoDB Commands
make mongo-up      # Start only MongoDB
make mongo-down    # Stop MongoDB
make mongo-reset   # Reset MongoDB data
make shell-mongo   # Access MongoDB shell
make ping-mongo    # Ping MongoDB

# PostgreSQL Commands
make postgres-up   # Start only PostgreSQL
make postgres-down # Stop PostgreSQL
make postgres-reset # Reset PostgreSQL data
make shell-postgres # Access PostgreSQL shell
make ping-postgres  # Ping PostgreSQL

# PostgreSQL Migrations (Alembic)
make migrate-generate MESSAGE="description"  # Generate new migration
make migrate-up    # Apply all pending migrations
make migrate-down  # Rollback one migration
make migrate-history # Show migration history
make migrate-current # Show current migration version
make migrate-reset # Reset all migrations (WARNING: destroys data)

# PostgreSQL Seeding
make seed          # Seed database with sample data
make seed-clear    # Clear all seeded data
make reseed        # Clear and reseed with fresh data

# Utilities
make shell         # Access Python container shell
make health        # Check application health
make version       # Show application version
make help          # Show all available commands (organized by category)
```

### Never Run Locally
- **DO NOT** run `poetry install` locally
- **DO NOT** run `uvicorn` or `python` commands locally
- **DO NOT** run `pytest`, `ruff`, or `pyright` commands locally
- **Always** use `make` commands which run everything in Docker containers
- The only exception is `make` itself, which orchestrates Docker containers

### Docker Services
- `python`: FastAPI application container
- `mongodb`: MongoDB NoSQL database container
- `postgresql`: PostgreSQL SQL database container
- All services defined in `docker-compose.development.yaml`

## Architecture Overview

### Clean Architecture + DDD + CQRS Pattern
This FastAPI application follows Clean Architecture with Domain-Driven Design tactical patterns and full CQRS:

**Layers (Inner to Outer):**
- **Domain Layer** (`app/core/domain/`): Aggregates, Entities, Value Objects, Domain Events, Specifications, Repository Interfaces (Protocols)
- **Application Layer** (`app/core/application/`): Commands, Queries, Handlers (CQRS), Read Models, Interfaces
- **Presentation Layer** (`app/presentation/`): API Controllers, DTOs, Dependencies
- **Infrastructure Layer** (`app/infrastructure/`): Database implementations, Event Bus, Mappers

**Database Strategy:**
- **PostgreSQL**: User entity (write/read with SQLModel + Alembic migrations)
- **MongoDB**: Log entity (audit trail with Beanie ODM)

### Technology Stack
- **Framework**: FastAPI with async support and dependency injection
- **Databases**:
  - **PostgreSQL** with SQLModel (SQL ORM) and Alembic (migrations)
  - **MongoDB** with Motor (async driver) and Beanie (ODM)
- **Containerization**: Docker with docker-compose for development and production
- **Code Quality**: Ruff for formatting and linting, Pyright for type checking
- **Testing**: pytest with pytest-asyncio and comprehensive mocking
- **Configuration**: Pydantic Settings with environment variables and global logging

### Key Architectural Decisions

**DDD Tactical Patterns**:
- **Aggregates**: Consistency boundaries (UserAggregate, LogAggregate)
- **Entities**: Objects with identity (User, Log)
- **Value Objects**: Immutable, self-validating (Email, Username, UserId)
- **Domain Events**: Trigger read model updates (UserCreated, UserUpdated, etc.)
- **Specifications**: Reusable business rules (UniqueEmailSpec, ActiveUserSpec)
- **Repository Interfaces**: Protocols for dependency inversion

**Full CQRS Pattern**:
- **Commands** (Write): CreateUserCommand, UpdateUserCommand, DeleteUserCommand
- **Command Handlers**: Execute writes via aggregates, publish domain events
- **Queries** (Read): GetUserQuery, ListUsersQuery
- **Query Handlers**: Read directly from optimized read models
- **Event Handlers**: Sync read models and create audit logs

**Dependency Injection**:
- Setter functions for runtime configuration (`set_user_repository()`)
- FastAPI Depends for request-scoped injection
- Protocol-based interfaces for loose coupling

**📝 Global Logging Configuration**: Centralized logging with datetime formatting:
- `app/infrastructure/configs/logging.py` provides comprehensive logging config
- Global application in `main.py` using `logging.config.dictConfig()`
- Use `logging.getLogger(__name__)` anywhere for consistent formatting

**Dual Database Integration**:
- **PostgreSQL**: User entity with SQLModel + Alembic migrations
- **MongoDB**: Log entity for audit trail with Beanie ODM
- Event-driven synchronization between write and read models
- Unified lifespan management in `app/infrastructure/setup.py`

**Docker-First Development**:
- All development commands run in Docker containers
- PostgreSQL and MongoDB services integrated with docker-compose
- **Modular Makefile** organized into separate files by functionality:
  - `makefiles/docker.mk` - Docker & environment management
  - `makefiles/quality.mk` - Code quality (format, lint, typecheck)
  - `makefiles/test.mk` - Testing commands
  - `makefiles/database.mk` - Database operations (PostgreSQL & MongoDB)
  - `makefiles/utils.mk` - Utilities (install, shell, logs, health)
  - `makefiles/workflow.mk` - Development workflows (dev, ci, verify)
- No local Python environment required

### Data Flow Pattern (CQRS)

**Write Path (Commands):**
1. **Request** → Controller (presentation layer)
2. **Controller** → Command Handler (application layer)
3. **Command Handler** → Aggregate (domain layer)
4. **Aggregate** → Write Repository (infrastructure layer)
5. **Write Repository** → PostgreSQL/MongoDB
6. **Domain Events** → Event Bus → Event Handlers
7. **Event Handlers** → Update Read Models + Create Logs

**Read Path (Queries):**
1. **Request** → Controller (presentation layer)
2. **Controller** → Query Handler (application layer)
3. **Query Handler** → Read Repository (infrastructure layer)
4. **Read Repository** → Optimized Read Model
5. **Response** ← DTO

### Environment Configuration
The application uses environment-based configuration with `.env` file support:
- Development: Auto-reload, debug mode, detailed logging
- Production: Optimized settings, security headers, structured logging
- Configurable via environment variables or `.env` file

### Database Strategy
**Dual Database Architecture** for flexibility and optimal data storage:

**PostgreSQL (Relational)**:
- SQLModel ORM for type-safe SQL operations
- Alembic for database migrations and schema versioning
- Structured data with foreign keys and constraints
- ACID transactions for data consistency
- Automatic table creation via migrations
- Database seeding system for sample/test data
- Connection pooling via async SQLAlchemy engine

**MongoDB (Document)**:
- Beanie ODM with Motor async driver
- Flexible schema for dynamic data
- Document-based storage for complex nested structures
- High performance for read-heavy workloads
- No migrations needed (schema-less)
- Automatic index creation

**Common Features**:
- Repository pattern abstracts data access for both databases
- UUID-based IDs support distributed systems
- Soft deletion preserves audit trail
- Indexes for performance optimization
- Unified lifespan management initializes both databases
- Async/await support throughout

### Testing Structure
- **Unit tests**: `tests/unit/` - Business logic with mocked dependencies
- **Integration tests**: `tests/integration/` - Real databases via testcontainers (isolated containers)
- **E2E tests**: `tests/e2e/` - Full API tests with test databases on running Docker services

**Test Database Strategy (Option 1)**:
- Uses separate database names on the same running Docker containers
- Development databases: `database_develop` (PostgreSQL), `backend_fastapi_app_dev` (MongoDB)
- Test databases: `database_test` (PostgreSQL), `backend_fastapi_app_test` (MongoDB)
- E2E tests automatically connect to test databases and clean up between tests

**Running Tests**:
```bash
make test              # Unit tests (mocked)
make test-integration  # Integration tests (testcontainers)
make test-e2e          # E2E tests (test databases on Docker services)
make setup-test-db     # Create test databases before first E2E run
```

- Command/Query handler testing with mock repositories
- pytest-asyncio for async test support
- pytest configuration in pyproject.toml
- All tests run in Docker containers via Makefile

## Important Implementation Details

### Modern Code Patterns

**Use Barrel Exports for Imports**:
```python
# ✅ Correct - Use barrel exports
from app.core.application.commands import CreateUserCommand
from app.core.application.queries import GetUserQuery, ListUsersQuery
from app.core.domain.exceptions import UserNotFound, UserAlreadyExists
from app.presentation.dtos import UserCreateRequest, UserResponse

# ❌ Avoid - Direct file imports
from app.core.application.commands.user.create_user import CreateUserCommand
```

**Use CQRS Handlers with Dependency Injection**:
```python
# ✅ Correct - FastAPI dependency injection with handlers
@router.post("/")
async def create_user(
    request: UserCreateRequest,
    handler: CreateUserHandler = Depends(get_create_user_handler)
):
    command = CreateUserCommand(email=request.email, ...)
    user_id = await handler.handle(command)
    return {"id": user_id}

# ❌ Avoid - Direct handler instantiation
handler = CreateUserHandler(...)  # Bypasses DI
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
# app/presentation/api/v1/__init__.py
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(user.router)

# app/presentation/api/v1/user.py
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

### Database Settings

**PostgreSQL**:
- `POSTGRE_DATABASE_URL`: PostgreSQL connection string (postgresql+asyncpg://...)
- Example: `postgresql+asyncpg://admin:password@postgresql:5432/database_develop`

**MongoDB**:
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
├── core/                 # 🎯 INNER LAYERS (no framework dependencies)
│   ├── domain/          # Layer 1: DOMAIN (DDD patterns)
│   │   ├── aggregates/      # Aggregate roots (UserAggregate, LogAggregate)
│   │   ├── entities/        # Entities (User, Log)
│   │   ├── value_objects/   # Value objects (Email, Username, UserId)
│   │   ├── events/          # Domain events (UserCreated, UserUpdated, etc.)
│   │   ├── specifications/  # Business rules (UniqueEmailSpec, ActiveUserSpec)
│   │   ├── services/        # Domain services
│   │   ├── repositories/    # Repository interfaces (Protocols)
│   │   └── exceptions/      # Domain exceptions
│   │
│   └── application/     # Layer 2: APPLICATION (CQRS)
│       ├── commands/        # Write side
│       │   ├── user/            # User commands (CreateUser, UpdateUser, etc.)
│       │   ├── log/             # Log commands
│       │   └── handlers/        # Command handlers
│       ├── queries/         # Read side
│       │   ├── user/            # User queries (GetUser, ListUsers)
│       │   ├── log/             # Log queries
│       │   └── handlers/        # Query handlers
│       ├── read_models/     # Optimized read models
│       └── interfaces/      # IEventBus, IPasswordHasher, etc.
│
├── presentation/         # Layer 3: PRESENTATION (interface adapters)
│   ├── api/             # REST API controllers
│   │   ├── v1/              # API version 1
│   │   │   ├── user.py          # User endpoints
│   │   │   └── log.py           # Log endpoints
│   │   └── system.py        # System endpoints (health, version)
│   ├── dependencies/    # FastAPI dependency injection
│   └── dtos/            # Data Transfer Objects
│
├── infrastructure/       # Layer 4: INFRASTRUCTURE (frameworks)
│   ├── configs/         # Configuration (app, logging, version)
│   ├── persistence/     # Database implementations
│   │   ├── postgresql/      # PostgreSQL (User entity)
│   │   │   ├── models/          # SQLModel models
│   │   │   ├── repositories/    # Write/Read repository implementations
│   │   │   ├── mappers/         # Entity <-> Model mappers
│   │   │   ├── migrations/      # Alembic migrations
│   │   │   ├── seeds/           # Database seeding
│   │   │   └── database.py      # Connection manager
│   │   └── mongodb/         # MongoDB (Log entity)
│   │       ├── models/          # Beanie models
│   │       ├── repositories/    # Write/Read repository implementations
│   │       ├── mappers/         # Entity <-> Model mappers
│   │       └── database.py      # Connection manager
│   ├── messaging/       # Event bus, password hasher
│   ├── event_handlers/  # Domain event handlers
│   ├── web/             # Web infrastructure (middleware, response utils, exception handlers)
│   └── setup.py         # Dependency injection setup
│
└── main.py               # Application entry point

tests/                    # 🧪 Test suite (outside app/)
├── unit/                # Unit tests
├── e2e/                 # End-to-end tests
└── conftest.py          # Shared fixtures
```

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.


      IMPORTANT: this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task.
