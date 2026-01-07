# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Workflow (Docker-First)

This project uses a **Docker-first development approach**. All commands run inside Docker containers.

### Quick Start
```bash
make dev       # Build and start all services with logs
make up        # Start services in background
make down      # Stop all services
make rebuild   # Rebuild and restart
```

### Essential Commands
```bash
# Code Quality (runs in Docker)
make format        # Format code with ruff
make lint          # Run linting
make typecheck     # Run type checking with pyright
make fix           # Format and fix all issues
make check         # Run all quality checks

# Testing (runs in Docker)
make test              # Run unit tests
make test-cov          # Run tests with coverage
make test-integration  # Run integration tests (testcontainers)
make test-e2e          # Run E2E tests (test databases)
make test-all          # Run all tests
make ci                # Full CI pipeline

# Run a single test
make shell                                        # Enter container
poetry run pytest tests/path/to/test.py::test_name -v  # Run specific test

# Database Management
make db-up             # Start PostgreSQL and MongoDB
make db-reset          # Reset all database data (WARNING: deletes all data)
make migrate-generate MESSAGE="description"  # Generate new migration
make migrate-up        # Apply pending migrations
make migrate-down      # Rollback one migration
make seed              # Seed database with sample data
make setup-test-db     # Create test databases before E2E tests
```

### Never Run Locally
- **DO NOT** run `poetry install`, `uvicorn`, `python`, `pytest`, `ruff`, or `pyright` locally
- **Always** use `make` commands which run everything in Docker containers

## Architecture Overview

### Clean Architecture + DDD + CQRS
```
┌─────────────────────────────────────────────────────┐
│              Presentation Layer                      │
│     (FastAPI Controllers, DTOs, Dependencies)        │
├─────────────────────────────────────────────────────┤
│              Application Layer                       │
│   (Commands, Queries, Handlers, Read Models)         │
├─────────────────────────────────────────────────────┤
│                Domain Layer                          │
│ (Aggregates, Entities, Value Objects, Domain Events) │
├─────────────────────────────────────────────────────┤
│             Infrastructure Layer                     │
│   (Repositories, Event Bus, Database Connections)    │
└─────────────────────────────────────────────────────┘
```

**Layers (Inner to Outer):**
- **Domain Layer** (`app/core/domain/`): Aggregates, Entities, Value Objects, Domain Events, Specifications, Repository Interfaces (Protocols)
- **Application Layer** (`app/core/application/`): Commands, Queries, Handlers (CQRS), Read Models, Interfaces
- **Presentation Layer** (`app/presentation/`): API Controllers, DTOs, Dependencies
- **Infrastructure Layer** (`app/infrastructure/`): Database implementations, Event Bus, Mappers

### Database Strategy
- **PostgreSQL**: User, Role, Permission entities (write/read with SQLModel + Alembic migrations)
- **MongoDB**: Log entity (audit trail with Beanie ODM)

### CQRS Data Flow

**Write Path (Commands):**
Request → Controller → Command Handler (with UoW) → Domain Service (validation) → Aggregate → Write Repository → Database → Domain Events → Event Handlers → Update Read Models + Create Logs

**Read Path (Queries):**
Request → Controller → Query Handler → Read Repository → Optimized Read Model → Response

### Key Patterns
- **Unit of Work**: Injected at controller, passed to handler's `handle()` method
- **Domain Services**: Stateless validation services (UserDomainService, RoleDomainService, PermissionDomainService)
- **Repository Access**: Command handlers access repos via UoW properties (e.g., `uow.users`, `uow.users_read`)

### Domain Entities
- **User**: Core user entity with email, username, password, active status
- **Role**: RBAC role (e.g., admin, user, moderator)
- **Permission**: RBAC permission (e.g., user:read, user:write)
- **Log**: Audit trail for domain events

## Important Implementation Patterns

### Use Barrel Exports
```python
# ✅ Correct
from app.core.application.commands import CreateUserCommand
from app.core.domain.exceptions import UserNotFound

# ❌ Avoid
from app.core.application.commands.user.create_user import CreateUserCommand
```

### Use CQRS Handlers with Unit of Work
```python
# ✅ Correct - Command handlers receive UoW as parameter
@router.post("/")
async def create_user(
    request: UserCreateRequest,
    handler: CreateUserHandlerDep,
    uow: UnitOfWorkDep,  # Unit of Work injected at controller level
):
    command = CreateUserCommand(email=request.email, ...)
    user_id = await handler.handle(command, uow)  # Pass UoW to handler
    return {"id": user_id}
    # Auto-commits on success, auto-rollback on exception

# ✅ Correct - Query handlers don't need UoW (read-only)
@router.get("/{user_id}")
async def get_user(
    user_id: str,
    handler: GetUserByIdHandlerDep,
):
    query = GetUserByIdQuery(user_id=user_id)
    user = await handler.handle(query)
    return user
```

### Unit of Work Pattern
```python
# Handler receives UoW - accesses repos via UoW properties
class CreateUserHandler:
    def __init__(self, password_hasher: IPasswordHasher) -> None:
        self._password_hasher = password_hasher
        # NO repositories in constructor - they come from UoW

    async def handle(self, command: CreateUserCommand, uow: IUnitOfWork) -> str:
        # Validate via domain service (pass read repo from UoW)
        await UserDomainService.validate_new_user(email, username, uow.users_read)

        # Create aggregate and persist via UoW
        aggregate = UserAggregate.create(...)
        await uow.users.save(aggregate)

        # Collect events (auto-published after commit)
        uow.collect_events(aggregate)

        return aggregate.id_str
        # NO manual commit - UoW auto-commits when request ends
```

### Domain Services (Stateless Validation)
```python
# ✅ Correct - Domain service with static methods
class UserDomainService:
    @staticmethod
    async def validate_new_user(
        email: Email,
        username: Username,
        user_read_repo: IUserReadRepository,  # Pass repo, not UoW
    ) -> None:
        await UserDomainService.ensure_email_unique(email, user_read_repo)
        await UserDomainService.ensure_username_unique(username, user_read_repo)

# ❌ Avoid - Domain service importing IUnitOfWork (causes circular imports)
```

### Logging Pattern
```python
import logging
logger = logging.getLogger(__name__)
logger.info("User created successfully")  # Never use print()
```

### DateTime Handling
```python
# ✅ Correct
from datetime import datetime, timezone
datetime.now(timezone.utc)

# ❌ Avoid (deprecated)
datetime.utcnow()
```

### Error Handling
Domain layer raises domain exceptions (never HTTPException). Presentation layer converts via exception handlers and `APIResponse` utility.

```python
# Domain layer
raise UserNotFound(user_id)

# Presentation layer converts to HTTP response automatically
```

### API Response Format
All responses follow standardized structure via `APIResponse`:
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { },
    "meta": { }
}
```

## API Endpoints

### System
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
- `GET /v1/users/{id}/roles` - Get user's assigned roles
- `POST /v1/users/{id}/roles` - Assign role to user
- `DELETE /v1/users/{id}/roles/{role_id}` - Remove role from user
- `GET /v1/users/{id}/permissions` - Get user's effective permissions
- `POST /v1/users/{id}/permissions` - Assign direct permission to user
- `DELETE /v1/users/{id}/permissions/{permission_id}` - Remove permission from user

### Role API (v1)
- `POST /v1/roles/` - Create new role
- `GET /v1/roles/` - List roles
- `GET /v1/roles/{id}` - Get role by ID
- `PUT /v1/roles/{id}` - Update role
- `DELETE /v1/roles/{id}` - Delete role
- `GET /v1/roles/{id}/permissions` - Get role's permissions
- `POST /v1/roles/{id}/permissions` - Assign permission to role
- `DELETE /v1/roles/{id}/permissions/{permission_id}` - Remove permission from role

### Permission API (v1)
- `POST /v1/permissions/` - Create new permission
- `GET /v1/permissions/` - List permissions
- `GET /v1/permissions/{id}` - Get permission by ID
- `PUT /v1/permissions/{id}` - Update permission
- `DELETE /v1/permissions/{id}` - Delete permission

### Log API (v1)
- `GET /v1/logs/` - List logs
- `GET /v1/logs/{id}` - Get log by ID

### API Documentation
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Testing

- **Unit tests** (`tests/unit/`): Business logic with mocked dependencies
- **Integration tests** (`tests/integration/`): Real databases via testcontainers
- **E2E tests** (`tests/e2e/`): Full API tests with test databases

Run `make setup-test-db` before first E2E test run to create test databases.

## Key Files

- `app/main.py` - Application entry point
- `app/infrastructure/setup.py` - Dependency injection setup and lifespan management
- `app/infrastructure/configs/` - Configuration (app, logging, version)
- `app/presentation/dependencies/` - FastAPI dependency providers
- `app/core/application/interfaces/unit_of_work.py` - IUnitOfWork Protocol interface
- `app/infrastructure/persistence/postgresql/unit_of_work.py` - PostgresUnitOfWork implementation
- `app/core/domain/services/` - Domain services (UserDomainService, RoleDomainService, PermissionDomainService)
- `app/core/application/commands/handlers/` - Command handlers (use UoW pattern)
- `alembic.ini` + `app/infrastructure/persistence/postgresql/migrations/` - Database migrations
- `makefiles/` - Modular Makefile includes (docker.mk, quality.mk, test.mk, database.mk, etc.)

## Environment Variables

### Application
- `APP_NAME`, `APP_VERSION`, `ENVIRONMENT`, `DEBUG`, `LOG_LEVEL`

### PostgreSQL
- `POSTGRE_DATABASE_URL`: Connection string (e.g., `postgresql+asyncpg://admin:password@postgresql:5432/database_develop`)

### MongoDB
- `MONGODB_URL`, `MONGODB_DB_NAME`, `MONGODB_TEST_DB_NAME`

### Server
- `HOST` (default: 0.0.0.0), `PORT` (default: 8080), `RELOAD`
