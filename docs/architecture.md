# Architecture Documentation

## Overview

This FastAPI application follows **Bounded Context (BC) Modular Monolith** with **Domain-Driven Design (DDD)** tactical patterns, **CQRS** (Command Query Responsibility Segregation), and the **Unit of Work** pattern. The architecture is structured around Bounded Contexts as the primary organizational axis, with each BC owning its own domain, application, infrastructure, and presentation layers.

The application is designed as a **template** that will scale to multiple BCs. Current BCs:
- **`iam`** (Identity & Access Management): authentication, RBAC authorization, user/role/permission/assignment
- **`audit`**: immutable audit trail, subscribes to IAM events via cross-BC event handler

---

## Bounded Context Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER (thin)                       │
│              FastAPI routers, DTOs, dependency providers            │
│                                                                     │
│  app/presentation/   ← system endpoints (/health-check, /version)   │
│  app/<bc>/presentation/   ← BC-specific API endpoints              │
├─────────────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER (per BC)                       │
│              CQRS commands, queries, handlers, UoW                  │
│                                                                     │
│  app/<bc>/application/   ← one folder per BC                        │
│    ├── commands/                                                     │
│    ├── queries/                                                      │
│    ├── handlers/                                                     │
│    ├── read_models/                                                  │
│    └── interfaces/   ← <BC>UnitOfWork, <BC>Repository interfaces     │
├─────────────────────────────────────────────────────────────────────┤
│                       DOMAIN LAYER (per BC)                         │
│         Aggregates, entities, value objects, events                 │
│                                                                     │
│  app/<bc>/domain/   ← pure business logic, no framework deps        │
│    ├── <aggregate>/   ← per-aggregate subfolder pattern             │
│    │   ├── aggregate.py                                               │
│    │   ├── entity.py                                                  │
│    │   ├── value_objects.py                                           │
│    │   ├── events.py                                                  │
│    │   ├── repository.py   ← Protocol interfaces                     │
│    │   ├── specifications.py   ← optional                             │
│    │   ├── exceptions.py                                              │
│    │   └── domain_service.py   ← optional                             │
│    └── specifications/   ← shared spec base (optional)                │
├─────────────────────────────────────────────────────────────────────┤
│                  INFRASTRUCTURE LAYER (per BC)                      │
│   Persistence, event handlers, third-party integrations              │
│                                                                     │
│  app/<bc>/infrastructure/   ← concrete implementations              │
│    ├── persistence/<db>/   ← models, mappers, repositories, UoW    │
│    ├── messaging/   ← password hasher, other adapters              │
│    └── event_handlers/   ← cross-BC translators                     │
├─────────────────────────────────────────────────────────────────────┤
│                      SHARED KERNEL                                 │
│             Cross-BC contracts (read-only)                          │
│                                                                     │
│  app/shared/                                                             │
│    ├── domain/   ← BaseEntity, BaseDomainEvent, base exceptions,    │
│    │           ID value objects (UserId, RoleId, etc.)               │
│    └── application/interfaces/   ← IUnitOfWork base, IEventBus,     │
│                                     ICommandBus, IQueryBus            │
├─────────────────────────────────────────────────────────────────────┤
│                     PLATFORM LAYER                                 │
│         Cross-cutting infrastructure (BC-agnostic)                   │
│                                                                     │
│  app/platform/                                                           │
│    ├── configs/                                                       │
│    ├── web/   ← FastAPI middleware, exception handlers,             │
│    │         response_dtos (generic response wrappers)               │
│    ├── persistence/<db>/   ← DB connection managers                 │
│    ├── messaging/event_bus.py   ← InMemoryEventBus implementation   │
│    └── messaging/services.py   ← app-scoped DI globals              │
├─────────────────────────────────────────────────────────────────────┤
│                  COMPOSITION ROOT                                   │
│              app/infrastructure/setup.py                             │
│         The ONLY place that imports from multiple BCs                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
app/
├── shared/                              # Shared Kernel — cross-BC contracts
│   ├── domain/
│   │   ├── base_entity.py              # BaseEntity (audit fields, soft delete)
│   │   ├── base_event.py               # BaseDomainEvent
│   │   ├── base_exception.py           # DomainException, EntityNotFound, EntityAlreadyExists
│   │   ├── error_codes.py              # ErrorCode enum
│   │   ├── validation.py               # ValidationError, BusinessRuleViolation
│   │   └── ids/
│   │       ├── user_id.py
│   │       ├── role_id.py
│   │       ├── permission_id.py
│   │       └── log_id.py
│   └── application/
│       └── interfaces/
│           ├── event_bus.py             # IEventBus
│           ├── command_bus.py           # ICommand, ICommandHandler, ICommandBus
│           ├── query_bus.py             # IQuery, IQueryHandler, IQueryBus
│           └── unit_of_work.py          # IUnitOfWork base protocol (no BC repos)
│
├── iam/                                 # BC: Identity & Access Management
│   ├── domain/
│   │   ├── user/                       # aggregate, entity, value_objects, events, etc.
│   │   ├── role/
│   │   ├── permission/
│   │   ├── assignment/                 # IAssignmentRepository + assignment events
│   │   └── specifications/              # Spec base class
│   ├── application/
│   │   ├── commands/{user,role,permission,assignment}/
│   │   ├── queries/{user,role,permission,assignment}/
│   │   ├── handlers/{user,role,permission,assignment}_handlers.py
│   │   ├── read_models/
│   │   └── interfaces/
│   │       ├── unit_of_work.py          # IIamUnitOfWork (extends IUnitOfWork + IAM repos)
│   │       └── password_hasher.py      # IPasswordHasher
│   ├── infrastructure/
│   │   ├── messaging/password_hasher.py # SimplePasswordHasher
│   │   └── persistence/postgresql/      # models, mappers, repositories, seeds, UoW
│   └── presentation/
│       ├── api/{user,role,permission}.py
│       ├── dependencies/{handlers,repositories}.py
│       └── dtos/{user,role,permission}.py
│
├── audit/                               # BC: Audit Logging
│   ├── domain/log/                      # aggregate, entity, value_objects (Action), events, repository
│   ├── application/
│   │   ├── commands/log/
│   │   ├── queries/log/
│   │   ├── handlers/{log_command,log_query}_handlers.py
│   │   └── read_models/
│   ├── infrastructure/
│   │   ├── persistence/mongodb/         # models, mappers, repositories
│   │   └── event_handlers/iam_event_translator.py  # cross-BC glue
│   └── presentation/{api,dependencies,dtos}/
│
├── platform/                            # Cross-cutting infrastructure (BC-agnostic)
│   ├── configs/                         # AppConfig, LoggingConfig, VersionConfig
│   ├── web/                             # middleware, exception handlers, response_dtos
│   ├── persistence/
│   │   ├── postgresql/database.py       # postgres_db_manager
│   │   └── mongodb/database.py          # mongo_db_manager
│   ├── messaging/event_bus.py           # InMemoryEventBus implementation
│   └── messaging/services.py            # get_password_hasher, get_event_bus globals
│
├── presentation/                        # System endpoints only
│   ├── api/system.py                    # /health-check, /version
│   └── dependencies/                    # (empty - BC-specific deps in each BC)
│
├── infrastructure/                      # Composition root
│   ├── setup.py                         # app_lifespan — wires all BCs together
│   └── persistence/seeders/             # CLI seeders
│
└── main.py                              # FastAPI app entry point
```

---

## DDD Tactical Patterns

### 1. Value Objects

Self-validating, immutable objects defined by their value:
- ID VOs (`UserId`, `RoleId`, etc.) in `app/shared/domain/ids/`
- Concept VOs (`Email`, `Username` for User) live with their aggregate
- `Action` (audit-specific) lives in `app/audit/domain/log/`

Frozen dataclasses with `__post_init__` validation, custom `__eq__`/`__hash__`.

### 2. Entities

Objects with identity and lifecycle. Located in `<bc>/domain/<aggregate>/entity.py`. Inherit from `BaseEntity` (shared) for audit fields.

### 3. Aggregates

Consistency boundaries that:
- Enforce invariants in their mutator methods
- Raise domain events on state changes
- Are reconstructed via `reconstitute()` from repositories (no events)
- Are created via `create()` factory (raises events)

Per-aggregate subfolder pattern:
```
iam/domain/user/
├── aggregate.py        # UserAggregate (factory + reconstitute + mutators + events)
├── entity.py           # User
├── value_objects.py    # Email, Username
├── events.py           # UserCreated, UserUpdated, ...
├── specifications.py   # ActiveUserSpecification, etc.
├── exceptions.py       # UserNotFound, UserAlreadyExists, InvalidUserState
├── repository.py       # IUserWriteRepository, IUserReadRepository
└── domain_service.py   # UserDomainService
```

### 4. Domain Events

Frozen dataclasses inheriting from `BaseDomainEvent` (shared). Carry a payload (`_payload()` method) for serialization. Examples:
- `UserCreated(user_id, email, username)`
- `RoleAssignedToUser(user_id, role_id)`
- `LogCreated(...)`

### 5. Repository Interfaces

Protocol-based interfaces in `<bc>/domain/<aggregate>/repository.py`. Concrete implementations live in `<bc>/infrastructure/persistence/`.

Per-BC split: write and read repositories are separate (`IUserWriteRepository`, `IUserReadRepository`) for CQRS clarity.

### 6. Unit of Work

Each BC has its own `<BC>UnitOfWork` extending the shared `IUnitOfWork` base:

```python
# Shared base (app/shared/application/interfaces/unit_of_work.py)
class IUnitOfWork(Protocol):
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, ...): ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
    def collect_events(self, aggregate: object) -> None: ...
    def add_event(self, event: BaseDomainEvent) -> None: ...

# BC-specific (app/iam/application/interfaces/unit_of_work.py)
class IIamUnitOfWork(IUnitOfWork, Protocol):
    users: IUserWriteRepository
    roles: IRoleWriteRepository
    permissions: IPermissionWriteRepository
    assignments: IAssignmentRepository
    users_read: IUserReadRepository
    # ...
```

The `PostgresIamUnitOfWork` (`app/iam/infrastructure/persistence/postgresql/unit_of_work.py`) implements this. One DB session = one IAM transaction = atomic across all IAM repos.

### 7. Domain Services

Cross-aggregate business logic. Located in `<bc>/domain/<aggregate>/domain_service.py` or at the BC root for BC-wide services.

---

## Cross-BC Communication

**Rule:** BCs communicate **only via domain events** through the `InMemoryEventBus`. BCs **never import each other directly**.

### The Cross-BC Event Flow

```
[BC A] Domain operation completes
  ↓
UoW commits to DB
  ↓
UoW publishes events via event_bus
  ↓
[BC B (consuming)] AuditUserEventTranslator receives event
  ↓
Translates to its own command (CreateLogCommand, etc.)
  ↓
[BC B] UoW commits to its own DB
```

### Example: IAM User Created → Audit Log Created

1. `POST /v1/users/` → `CreateUserHandler.handle(command, iam_uow)`
2. `UserAggregate.create()` → `UserCreated` event queued
3. `iam_uow.commit()` → Postgres commits → publishes `UserCreated` via event_bus
4. `AuditUserEventTranslator.on_user_created(UserCreated)` (subscribed in `setup.py`)
5. Translates to `CreateLogCommand(action="user_created", user_id=..., metadata=...)`
6. `CreateLogHandler.handle(command)` → MongoLogWriteRepository → MongoDB commits

### Enforced by `import-linter`

The `pyproject.toml` has 8 architectural contracts that fail CI if violated:
- BCs cannot import each other (BC isolation)
- Each BC has internal layer boundaries (presentation → application → domain)
- Domain layer has no infrastructure/framework imports
- Shared kernel has no BC dependencies
- Platform cannot import BC domain/application

---

## CQRS Pattern

### Command Side (Write Path)

```
HTTP Request → Controller → Command Handler (with UoW) → Aggregate → Write Repository → Database
                                    ↓
                            Domain Events → Event Bus → (cross-BC translators)
```

### Query Side (Read Path)

```
HTTP Request → Controller → Query Handler → Read Repository → Database → DTO → Response
```

### Per-BC Handler Pattern

Each command handler `handle(command, uow: <BC>UnitOfWork)`:
1. Construct value objects (validates format)
2. Call domain service for cross-aggregate validation
3. Call aggregate factory (raises events)
4. Persist via `uow.<repo>.save(aggregate)`
5. `uow.collect_events(aggregate)` (events published after commit)

---

## Dependency Injection

### Per-BC Dependency Providers

Each BC has its own `presentation/dependencies/` folder with:
- `handlers.py` — handler factory functions + `<Handler>Dep` type aliases
- `repositories.py` — `<BC>UnitOfWorkDep`, read-model repository deps

Example:
```python
# app/iam/presentation/dependencies/repositories.py
async def get_iam_unit_of_work() -> AsyncGenerator[IIamUnitOfWork, None]:
    uow = PostgresIamUnitOfWork(
        session_factory=postgres_db_manager.session_maker,
        event_bus=get_event_bus(),
    )
    async with uow:
        yield uow

IamUnitOfWorkDep = Annotated[IIamUnitOfWork, Depends(get_iam_unit_of_work)]
```

### Composition Root

`app/infrastructure/setup.py` is the **only place** that wires across BCs:
1. Connects platform databases
2. Creates the shared `InMemoryEventBus`
3. Subscribes cross-BC event translators (audit subscribes to IAM)
4. Sets app-scoped DI globals (`get_event_bus`, `get_password_hasher`)

---

## Architectural Rules (enforced by import-linter)

| # | Rule | Type |
|---|---|---|
| 1 | Shared kernel has no BC/platform/presentation/infrastructure dependencies | forbidden |
| 2 | Platform cannot import BC domain/application code | forbidden |
| 3 | IAM layer boundaries: `presentation → application → domain` | layers |
| 4 | IAM domain has no infrastructure or framework imports | forbidden |
| 5 | IAM does not import from audit BC | forbidden |
| 6 | Audit layer boundaries: `presentation → application → domain` | layers |
| 7 | Audit domain has no infrastructure or framework imports | forbidden |
| 8 | Audit does not import from IAM BC (except the cross-BC translator) | forbidden |

Run `make arch-check` to verify all 8 contracts are kept.

---

## Adding a New Bounded Context

To add a new BC (e.g., `billing`):

1. Create folder structure:
   ```
   app/billing/
   ├── domain/{aggregate}/
   ├── application/{commands,queries,handlers,read_models,interfaces}/
   ├── infrastructure/persistence/{db}/
   └── presentation/{api,dependencies,dtos}/
   ```

2. Define `<BC>UnitOfWork` extending `IUnitOfWork`

3. Implement `<BC>UnitOfWork` in `infrastructure/persistence/<db>/unit_of_work.py`

4. Add `app/billing` router to `app/main.py`

5. Add `import-linter` contracts:
   - `<BC> layer boundaries`
   - `<BC> domain has no infrastructure imports`
   - `<BC> does not import from iam/audit`

6. Add cross-BC subscriptions in `app/infrastructure/setup.py` (if needed)

7. Mirror test structure in `tests/<bc>/`:
   - `tests/<bc>/unit/` — pure unit tests
   - `tests/<bc>/integration/` — DB-backed tests
   - `tests/<bc>/e2e/` — full API tests

8. Add Makefile target `test-<bc>` (e.g., `test-billing`)

---

## Key Files

| Purpose | Path |
|---|---|
| FastAPI entry | `app/main.py` |
| Composition root | `app/infrastructure/setup.py` |
| Shared kernel | `app/shared/domain/`, `app/shared/application/interfaces/` |
| IAM domain | `app/iam/domain/{user,role,permission,assignment}/` |
| IAM application | `app/iam/application/{commands,queries,handlers,read_models,interfaces}/` |
| IAM infrastructure | `app/iam/infrastructure/persistence/postgresql/` |
| IAM presentation | `app/iam/presentation/{api,dependencies,dtos}/` |
| Audit domain | `app/audit/domain/log/` |
| Audit application | `app/audit/application/{commands,queries,handlers,read_models}/` |
| Audit infrastructure | `app/audit/infrastructure/persistence/mongodb/` |
| Audit cross-BC | `app/audit/infrastructure/event_handlers/iam_event_translator.py` |
| Architecture enforcement | `pyproject.toml` (`[tool.importlinter]`) |
| Pre-commit hook | `.pre-commit-config.yaml` |
| Make targets | `makefiles/quality.mk`, `makefiles/test.mk` |
