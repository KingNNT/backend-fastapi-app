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
make arch-check    # Run architectural rules (import-linter) - 8 contracts
make fix           # Format and fix all issues
make check         # Run all quality checks

# Testing (runs in Docker)
make test              # Run unit tests
make test-cov          # Run tests with coverage
make test-iam          # Run IAM BC tests only
make test-audit        # Run Audit BC tests only
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

### Bounded Context Modular Monolith + DDD + CQRS

The codebase is organized around **Bounded Contexts** (BCs). Each BC owns its own 4 layers (domain, application, infrastructure, presentation). Cross-BC communication flows through domain events on a shared event bus — BCs never import each other.

```
┌─────────────────────────────────────────────────────────────────────┐
│              PRESENTATION LAYER (per BC)                            │
│        FastAPI routers, DTOs, dependency providers                  │
│  app/<bc>/presentation/{api,dependencies,dtos}/                     │
│  app/presentation/   ← system endpoints (health, version)            │
├─────────────────────────────────────────────────────────────────────┤
│              APPLICATION LAYER (per BC)                             │
│        CQRS commands, queries, handlers, <BC>UnitOfWork              │
│  app/<bc>/application/{commands,queries,handlers,read_models,interfaces}/│
├─────────────────────────────────────────────────────────────────────┤
│                  DOMAIN LAYER (per BC)                               │
│  Aggregates, entities, value objects, events (pure logic)           │
│  app/<bc>/domain/<aggregate>/                                      │
├─────────────────────────────────────────────────────────────────────┤
│              INFRASTRUCTURE LAYER (per BC)                          │
│  Persistence (Postgres/Mongo), mappers, repos, UoW, cross-BC glue  │
│  app/<bc>/infrastructure/                                          │
├─────────────────────────────────────────────────────────────────────┤
│                     SHARED KERNEL                                   │
│  Base classes, ID VOs, bus interfaces, base UoW (cross-BC contracts) │
│  app/shared/                                                        │
├─────────────────────────────────────────────────────────────────────┤
│                      PLATFORM LAYER                                 │
│  Configs, web, DB managers, event bus impl, services (BC-agnostic)  │
│  app/platform/                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Current Bounded Contexts:**
- **`app/iam/`** — Identity & Access Management (User, Role, Permission, Assignment)
- **`app/audit/`** — Audit Logging (Log + cross-BC translator for IAM events)
- **`app/shared/`** — Shared Kernel (BaseEntity, ID VOs, IUnitOfWork base, bus interfaces)
- **`app/platform/`** — Platform infrastructure (configs, web middleware, DB managers)
- **`app/presentation/`** — System endpoints only (health-check, version)
- **`app/infrastructure/`** — Composition root (`setup.py` wires all BCs together)

**Layers (Inner to Outer, enforced by `import-linter`):**
- **Domain Layer** (`app/<bc>/domain/`): Aggregates, Entities, Value Objects, Domain Events, Repository Protocols — no framework deps
- **Application Layer** (`app/<bc>/application/`): Commands, Queries, Handlers, Read Models, `<BC>UnitOfWork` interface
- **Presentation Layer** (`app/<bc>/presentation/`): API Controllers, DTOs, Dependencies
- **Infrastructure Layer** (`app/<bc>/infrastructure/`): Concrete persistence, event handlers, cross-BC glue

### Database Strategy
- **PostgreSQL**: IAM entities (User, Role, Permission, Assignment) via SQLModel + Alembic migrations
- **MongoDB**: Audit Log entity via Beanie ODM

### CQRS Data Flow

**Write Path (Commands) — Cross-BC:**
```
[BC A] HTTP Request → Controller → Command Handler (with UoW)
       ↓
       Domain Service (validation) → Aggregate → UoW Repo → Database
       ↓
       UoW commits → publishes Domain Events via event_bus
       ↓
[BC B] AuditUserEventTranslator.on_X(event) → Build CreateLogCommand
       ↓
       CreateLogHandler.handle(command) → MongoDB
```

**Read Path (Queries):**
```
HTTP Request → Controller → Query Handler → Read Repository → Optimized Read Model → Response
```

### Key Patterns
- **Per-BC Unit of Work**: Each BC has its own `<BC>UnitOfWork` (e.g., `IIamUnitOfWork`) extending `IUnitOfWork` from shared. Inject at controller, pass to handler's `handle()` method.
- **Per-aggregate subfolder pattern** inside `<bc>/domain/<aggregate>/`: aggregate.py, entity.py, value_objects.py, events.py, repository.py, etc.
- **Repository Access**: Command handlers access repos via UoW properties (`uow.users`, `uow.assignments`, etc.)
- **Cross-BC Communication**: ONLY via `IEventBus`. Never import another BC directly.

### Domain Aggregates
- **User** (IAM): Core user entity with email, username, password, active status
- **Role** (IAM): RBAC role (e.g., admin, user, moderator)
- **Permission** (IAM): RBAC permission (e.g., user:read, user:write)
- **Assignment** (IAM): Junction concepts (user_has_role, role_has_permission, user_has_permission)
- **Log** (Audit): Immutable audit trail of cross-BC events

## Important Implementation Patterns

### Use Barrel Exports
```python
# ✅ Correct - per BC barrel exports
from app.iam.application.commands import CreateUserCommand, AssignRoleToUserCommand
from app.iam.domain.user.exceptions import UserNotFound
from app.iam.application.handlers import CreateUserHandlerDep

# ❌ Avoid - deep imports
from app.iam.application.commands.user.create_user import CreateUserCommand

# ❌ NEVER - cross-BC imports (forbidden by import-linter)
from app.audit.domain.log import LogAggregate  # in IAM code
from app.iam.domain.user import User  # in audit code
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
# Handler receives <BC>UnitOfWork - accesses BC-specific repos via UoW properties
class CreateUserHandler:
    def __init__(self, password_hasher: IPasswordHasher) -> None:
        self._password_hasher = password_hasher
        # NO repositories in constructor - they come from UoW

    async def handle(self, command: CreateUserCommand, uow: IIamUnitOfWork) -> str:
        # Validate via domain service (pass read repo from UoW)
        await UserDomainService.validate_new_user(email, username, uow.users_read)

        # Create aggregate and persist via UoW
        aggregate = UserAggregate.create(...)
        await uow.users.save(aggregate)
        uow.collect_events(aggregate)  # events published after commit

        return aggregate.id_str
```

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

### Entry Point & Composition Root
- `app/main.py` - FastAPI app entry point; includes BC routers
- `app/infrastructure/setup.py` - **Composition root**: connects DBs, wires cross-BC event subscriptions, sets DI globals

### Shared Kernel
- `app/shared/domain/base_entity.py` - BaseEntity (audit fields, soft delete)
- `app/shared/domain/base_event.py` - BaseDomainEvent
- `app/shared/domain/base_exception.py` - DomainException hierarchy
- `app/shared/domain/ids/` - UserId, RoleId, PermissionId, LogId (cross-BC identity contracts)
- `app/shared/application/interfaces/` - IEventBus, ICommandBus, IQueryBus, IUnitOfWork (base)

### IAM Bounded Context (`app/iam/`)
- `app/iam/domain/{user,role,permission,assignment}/` - Per-aggregate subfolder pattern (aggregate, entity, value_objects, events, etc.)
- `app/iam/application/handlers/` - CQRS command/query handlers
- `app/iam/application/interfaces/unit_of_work.py` - **IIamUnitOfWork** (extends base with user/role/permission/assignment repos)
- `app/iam/infrastructure/persistence/postgresql/unit_of_work.py` - **PostgresIamUnitOfWork** implementation
- `app/iam/infrastructure/messaging/password_hasher.py` - SimplePasswordHasher
- `app/iam/presentation/` - FastAPI routers, DTOs, dependency providers for IAM

### Audit Bounded Context (`app/audit/`)
- `app/audit/domain/log/` - Log aggregate, entity, Action value object, LogCreated event, ILogRepository
- `app/audit/application/handlers/` - CreateLogHandler, GetLogByIdHandler, ListLogsHandler
- `app/audit/infrastructure/persistence/mongodb/` - MongoDB models, mappers, repositories
- `app/audit/infrastructure/event_handlers/iam_event_translator.py` - **AuditUserEventTranslator**: cross-BC glue that subscribes to IAM events and translates to audit commands
- `app/audit/presentation/` - Log API endpoints

### Platform Layer
- `app/platform/configs/` - AppConfig, LoggingConfig, VersionConfig
- `app/platform/web/` - FastAPI middleware, exception handlers, generic response DTOs
- `app/platform/persistence/postgresql/database.py` - postgres_db_manager
- `app/platform/persistence/mongodb/database.py` - mongo_db_manager
- `app/platform/messaging/event_bus.py` - InMemoryEventBus implementation
- `app/platform/messaging/services.py` - App-scoped DI globals (get_event_bus, get_password_hasher)

### Build & Quality Tools
- `pyproject.toml` - **`[tool.importlinter]` section**: 8 architectural contracts (BC isolation, layer boundaries, domain purity, shared kernel discipline, platform isolation)
- `.pre-commit-config.yaml` - Pre-commit hooks including import-linter
- `alembic.ini` + `app/iam/infrastructure/persistence/postgresql/migrations/` - PostgreSQL migrations
- `makefiles/` - Modular Makefile includes (docker.mk, quality.mk, test.mk, database.mk, workflow.mk)

## Environment Variables

### Application
- `APP_NAME`, `APP_VERSION`, `ENVIRONMENT`, `DEBUG`, `LOG_LEVEL`

### PostgreSQL
- `POSTGRE_DATABASE_URL`: Connection string (e.g., `postgresql+asyncpg://admin:password@postgresql:5432/database_develop`)

### MongoDB
- `MONGODB_URL`, `MONGODB_DB_NAME`, `MONGODB_TEST_DB_NAME`

### Server
- `HOST` (default: 0.0.0.0), `PORT` (default: 8080), `RELOAD`
