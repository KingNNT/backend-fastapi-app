# Bounded Context Modular Monolith Refactor — Design Spec

- **Date**: 2026-06-21
- **Status**: Approved (pending spec review)
- **Branch**: `refactor/bc-modular-monolith`
- **Author**: kingnnt (via brainstorming session)
- **Target version**: `v0.2.0-bc-modular`

---

## 1. Motivation

This project is a **template** for backend applications using FastAPI. It already implements DDD tactical patterns (aggregates, value objects, domain events, repositories, specifications) and CQRS on top of a Clean Architecture layer split. However, the current structure is **layer-first**:

```
app/
├── core/
│   ├── domain/        ← all aggregates, VOs, events, repos, specs for every concept
│   └── application/   ← all commands, queries, handlers
├── presentation/      ← all routers, DTOs, DI for every concept
└── infrastructure/    ← all DB implementations
```

### Pain points identified

1. **No domain-level isolation.** `User`, `Role`, `Permission`, `Log` aggregates live together under one `domain/` folder with no explicit boundary between business capabilities.
2. **Upcoming scope expansion.** New domains (e.g., Billing, Inventory, Notifications) are planned. Adding them under the current structure will produce an ever-growing `domain/aggregates/` folder with no clear ownership.
3. **Microservice extraction planned.** Some BCs are candidates for extraction into separate services. The current structure would require a costly refactoring of import paths at extraction time.
4. **Template must teach the right pattern.** A template that mixes all aggregates in one `domain/` folder teaches newcomers an anti-pattern: "every aggregate is a file, BCs don't exist".

### Goals

- Reorganize the codebase around **Bounded Contexts** (BCs) as the primary structural axis.
- Make each BC a **self-contained mini-module** with its own 4 layers.
- Keep cross-BC communication **strictly via domain events** (only the composition root wires them).
- **Enforce** BC and layer boundaries via tooling, not just comments.
- Preserve every existing feature and test through a **phased, hard-cut** migration.

### Non-goals

- No change to business behavior. All endpoints, all aggregates, all events behave identically after the refactor.
- No change to the database schema.
- No introduction of new features.
- No backward-compatibility shims (we accept a hard cut at each phase).

---

## 2. Bounded Context Decomposition

### 2.1 BCs identified

| BC | Name | Purpose | Concepts (aggregates) |
|---|---|---|---|
| `iam` | Identity & Access Management | Authentication + RBAC authorization | `User`, `Role`, `Permission`, `Assignment` (relationship concept) |
| `audit` | Audit Logging | Immutable audit trail | `Log` |
| `shared` | Shared Kernel | Cross-BC contracts only | `BaseEntity`, `BaseEvent`, `ID` value objects, `IUnitOfWork` base, `IEventBus`, `ICommandBus`, `IQueryBus` |
| `platform` | Platform / Cross-cutting Infrastructure | Framework glue not owned by any BC | DB connection managers, FastAPI middleware, exception handlers, `InMemoryEventBus`, CLI |

### 2.2 Why this decomposition (not per-aggregate)

The four aggregates `User`, `Role`, `Permission`, `Assignment` form a single business capability ("who can do what"). They share a ubiquitous language, are owned by the same team, and are validated together. Splitting them into separate BCs would:
- Create artificial boundaries
- Force cross-BC existence checks (`user_exists()`) on every assignment operation
- Complicate future microservice extraction (distributed transactions)

`Log` is already physically separated (MongoDB vs PostgreSQL) and is populated exclusively via domain events — it is a natural BC of its own.

### 2.3 BC interaction contract

- **BCs are forbidden from importing each other.** Enforced by `import-linter` (see §7).
- **Cross-BC communication is via domain events only.** IAM publishes `UserCreated`, `UserUpdated`, etc.; Audit subscribes to them.
- **Cross-BC event handlers live in the consuming BC.** `AuditUserEventTranslator` lives in `audit/infrastructure/event_handlers/`, not in `iam/` or `platform/`.
- **The composition root (`app/infrastructure/setup.py`) is the only place that imports from multiple BCs.** It wires subscriptions.
- **Shared kernel (`app/shared/`) is read-only from BCs.** BCs may import from `shared/`; `shared/` may never import from any BC.

---

## 3. Target Folder Structure

```
app/
├── shared/                                    # Shared Kernel (cross-BC contracts)
│   ├── domain/
│   │   ├── base_entity.py                     # BaseEntity (audit fields, soft delete)
│   │   ├── base_event.py                      # BaseDomainEvent
│   │   ├── base_exception.py                  # DomainException, ErrorCode
│   │   ├── validation.py                      # ValidationError, InvalidStateError
│   │   └── ids/
│   │       ├── user_id.py
│   │       ├── role_id.py
│   │       ├── permission_id.py
│   │       └── log_id.py
│   └── application/
│       └── interfaces/
│           ├── event_bus.py                   # IEventBus
│           ├── command_bus.py                 # ICommand, ICommandHandler, ICommandBus
│           ├── query_bus.py                   # IQuery, IQueryHandler, IQueryBus
│           └── unit_of_work.py                # IUnitOfWork base protocol (no repos)
│
├── iam/                                       # BC: Identity & Access Management
│   ├── domain/
│   │   ├── user/                              # per-aggregate subfolder pattern
│   │   │   ├── aggregate.py                   # UserAggregate
│   │   │   ├── entity.py                      # User
│   │   │   ├── value_objects.py               # Email, Username
│   │   │   ├── events.py                      # UserCreated, UserUpdated...
│   │   │   ├── specifications.py              # ActiveUserSpecification...
│   │   │   ├── exceptions.py                  # UserNotFound, UserAlreadyExists, InvalidUserState
│   │   │   ├── repository.py                  # IUserWriteRepository, IUserReadRepository
│   │   │   └── domain_service.py              # UserDomainService
│   │   ├── role/                              # same structure
│   │   ├── permission/                        # same structure
│   │   └── assignment/
│   │       ├── exceptions.py
│   │       ├── events.py                      # RoleAssignedToUser, PermissionAssignedToRole...
│   │       └── repository.py                  # IAssignmentRepository
│   ├── application/
│   │   ├── commands/{user,role,permission,assignment}/
│   │   ├── queries/{user,role,permission,assignment}/
│   │   ├── handlers/{user,role,permission,assignment}_handlers.py
│   │   ├── read_models/
│   │   └── interfaces/
│   │       ├── password_hasher.py             # IPasswordHasher
│   │       └── unit_of_work.py                # IIamUnitOfWork
│   ├── infrastructure/
│   │   ├── persistence/postgresql/
│   │   │   ├── models/
│   │   │   ├── mappers/
│   │   │   ├── repositories/                  # user_write, user_read, role_*, permission_*, assignment
│   │   │   ├── unit_of_work.py                # PostgresIamUnitOfWork
│   │   │   └── helpers.py
│   │   ├── messaging/password_hasher.py
│   │   └── event_handlers/                    # (internal IAM handlers, if any)
│   └── presentation/
│       ├── api/{user,role,permission,assignment}.py
│       ├── dependencies/{handlers,repositories,services}.py
│       └── dtos/{user,role,permission,assignment,response}.py
│
├── audit/                                     # BC: Audit Logging
│   ├── domain/log/
│   │   ├── aggregate.py
│   │   ├── entity.py
│   │   ├── value_objects.py                   # Action
│   │   ├── events.py
│   │   ├── exceptions.py
│   │   └── repository.py
│   ├── application/...
│   ├── infrastructure/
│   │   ├── persistence/mongodb/...
│   │   └── event_handlers/
│   │       └── iam_event_handlers.py          # AuditUserEventTranslator (subscribes to IAM events)
│   └── presentation/...
│
├── platform/                                  # Cross-cutting infrastructure (BC-agnostic)
│   ├── configs/
│   ├── web/                                   # middleware, exception_handlers, response (APIResponse)
│   ├── persistence/
│   │   ├── postgresql/database.py             # postgres_db_manager
│   │   └── mongodb/database.py                # mongo_db_manager
│   ├── messaging/event_bus.py                 # InMemoryEventBus implementation
│   └── cli/
│
├── infrastructure/                            # Composition root
│   └── setup.py                               # app_lifespan — the ONLY cross-BC wiring point
│
└── main.py                                    # FastAPI entry point
```

### 3.1 Per-aggregate subfolder pattern (inside a BC)

Each aggregate is a self-contained mini-package with these files (omit any that don't apply):

| File | Contents |
|---|---|
| `aggregate.py` | Aggregate root (factory methods, invariants, event collection) |
| `entity.py` | Domain entity (identity + lifecycle) |
| `value_objects.py` | Value objects specific to this aggregate |
| `events.py` | Domain events raised by this aggregate |
| `specifications.py` | Specification pattern implementations |
| `exceptions.py` | Aggregate-specific domain exceptions |
| `repository.py` | Repository Protocol interfaces (read + write) |
| `domain_service.py` | Cross-entity business logic (optional) |

This pattern is **the template's reusable unit** — copying `iam/domain/user/` and renaming it produces a new aggregate scaffold.

---

## 4. Unit of Work & Event Flow

### 4.1 UoW hierarchy

```
IUnitOfWork (shared/application/interfaces/unit_of_work.py)
    Protocol: __aenter__, __aexit__, commit, rollback, collect_events, add_event
        │
        ├── IIamUnitOfWork (iam/application/interfaces/unit_of_work.py)
        │   Adds attributes: users, users_read, roles, roles_read,
        │                    permissions, permissions_read, assignments
        │   Implemented by: PostgresIamUnitOfWork
        │
        └── IAuditUnitOfWork (audit/application/interfaces/unit_of_work.py)
            Adds attributes: logs, logs_read
            Implemented by: MongoAuditUnitOfWork
```

### 4.2 Behavioral contract

- `__aenter__` creates a new DB session and instantiates all repositories sharing that session.
- `__aexit__`:
  - On exception → `rollback()` + discard collected events
  - On success → `commit()` (DB persist) → `_publish_events()` (publish via event bus)
- Events are **only** published after a successful commit — never on rollback.
- `collect_events(aggregate)` drains an aggregate's events into the UoW and clears the aggregate's list.
- Event publishing is **best-effort** after commit — failure to publish does not roll back the transaction (audit log lag is preferable to losing a committed user).

### 4.3 Fix: Assignment handlers now use the UoW

**Before** (current code): Assignment handlers (`AssignRoleToUserHandler`, etc.) take an `IAssignmentRepository` and `IEventBus` directly via constructor injection — no transaction boundary.

**After**: Assignment handlers take `uow: IIamUnitOfWork` as a `handle()` parameter, exactly like `CreateUserHandler`. The assignment repository lives inside the UoW (`uow.assignments`), and assignment events are collected via `uow.collect_events()`. This closes the transactional gap.

### 4.4 End-to-end event flow (Create User)

```
1. POST /v1/users/
2. iam/presentation/api/user.py → injects CreateUserHandlerDep, IamUnitOfWorkDep
3. CreateUserHandler.handle(cmd, uow)
   - Email/Username value-object validation
   - UserDomainService.validate_new_user (uses uow.users_read)
   - UserAggregate.create() → UserCreated event collected
   - uow.users.save(aggregate)
   - uow.collect_events(aggregate)
4. __aexit__ (success):
   - session.commit() (Postgres transaction atomic)
   - _publish_events() → event_bus.publish(UserCreated)
5. AuditUserEventTranslator.on_user_created(UserCreated) [in audit/infrastructure/event_handlers/]
   - Builds CreateLogCommand(action="USER_CREATED", ...)
   - Opens IAuditUnitOfWork, calls CreateLogHandler.handle(cmd, audit_uow)
6. audit_uow.commit() → Mongo insert
7. Response 201 Created
```

If step 6 fails (Mongo down): the user is already committed; audit log is missing. This matches current behavior and is acceptable for an audit trail.

---

## 5. Presentation & Dependency Injection

### 5.1 Per-BC dependency providers

Each BC owns its own dependency provider files. There is no central `presentation/dependencies/handlers.py` anymore.

```
app/iam/presentation/dependencies/
├── handlers.py        # IAM handler factory functions + *HandlerDep aliases
├── repositories.py    # IamUnitOfWorkDep, repo factories (request-scoped)
└── services.py        # PasswordHasherDep

app/audit/presentation/dependencies/
├── handlers.py
└── repositories.py    # AuditUnitOfWorkDep
```

### 5.2 Request-scoped UoW via FastAPI Depends

```python
# iam/presentation/dependencies/repositories.py
async def get_iam_unit_of_work(
    event_bus: IEventBus = Depends(get_event_bus),
) -> AsyncGenerator[IIamUnitOfWork, None]:
    uow = PostgresIamUnitOfWork(
        session_factory=postgres_db_manager.session_maker,
        event_bus=event_bus,
    )
    async with uow:                       # auto-commit on success, rollback on exception
        yield uow

IamUnitOfWorkDep = Annotated[IIamUnitOfWork, Depends(get_iam_unit_of_work)]
```

### 5.3 Composition root

`app/infrastructure/setup.py` is the **only** file allowed to import from multiple BCs. It:
1. Connects platform databases
2. Creates the shared `InMemoryEventBus`
3. Wires cross-BC subscriptions (audit subscribes to IAM events via `AuditUserEventTranslator`)
4. Sets app-scoped deps (`event_bus`, `password_hasher`)

### 5.4 Router aggregation

Each BC exposes one aggregated router from its `presentation/api/__init__.py`. `main.py` includes each BC's router with a `/v1` prefix.

---

## 6. Testing Strategy

### 6.1 Mirror structure

`tests/` mirrors the BC structure of `app/`:

```
tests/
├── conftest.py                    # root: event_bus fixture, DB URLs
├── shared/                        # tests for shared kernel
│   └── domain/{test_base_entity.py, test_ids.py}
├── iam/
│   ├── conftest.py                # IAM fixtures (iam_uow_mock, password_hasher)
│   ├── unit/
│   │   ├── domain/{user,role,permission,assignment}/...
│   │   └── application/test_*_handlers.py
│   ├── integration/               # testcontainers, no HTTP
│   │   ├── conftest.py
│   │   ├── test_user_repository.py
│   │   ├── test_role_repository.py
│   │   ├── test_permission_repository.py
│   │   ├── test_assignment_repository.py
│   │   └── test_iam_unit_of_work.py
│   └── e2e/
│       └── test_{user,role,permission,assignment}_api.py
├── audit/
│   ├── unit/...
│   ├── integration/...
│   └── e2e/test_log_api.py
├── integration/                   # cross-BC integration tests
│   └── test_cross_bc_event_flow.py
└── platform/
    └── test_event_bus.py
```

### 6.2 Test types

| Type | Location | Scope | I/O |
|---|---|---|---|
| Unit | `tests/<bc>/unit/` | One aggregate/handler/VO | None (mock UoW) |
| Integration | `tests/<bc>/integration/` | One BC + its DB | testcontainers, no HTTP |
| E2E | `tests/<bc>/e2e/` | One BC's API | AsyncClient + test DB |
| Cross-BC | `tests/integration/` | Multiple BCs | Both DBs up |

### 6.3 Makefile additions

```makefile
test-iam:        ## Run IAM tests only
	$(DOCKER) poetry run pytest tests/iam/ -v
test-audit:      ## Run Audit tests only
	$(DOCKER) poetry run pytest tests/audit/ -v
test-unit:       ## Run unit tests across all BCs
	$(DOCKER) poetry run pytest tests/ tests/*/unit/ -v
test-integration: ## Run integration tests (per-BC + cross-BC)
	$(DOCKER) poetry run pytest tests/*/integration/ tests/integration/ -v
test-e2e:        ## Run E2E tests
	$(DOCKER) poetry run pytest tests/*/e2e/ -v
```

---

## 7. Architectural Rules Enforcement

### 7.1 Tooling

- **`import-linter`** (new dependency): enforces BC boundaries and intra-BC layer rules by analyzing the import graph.
- **Ruff** (existing): format + import order.
- **Pyright** (existing): type safety + Protocol contracts.

### 7.2 Contracts (in `pyproject.toml`)

| # | Contract | Type | Purpose |
|---|---|---|---|
| 1 | IAM ↔ Audit forbidden imports | `forbidden` | BC independence |
| 2 | Shared kernel cannot import BCs | `forbidden` | Keep shared pure |
| 3 | Platform cannot import BCs | `forbidden` | Platform is BC-agnostic |
| 4 | IAM layer boundaries | `layers` | `presentation → application → domain` |
| 5 | Audit layer boundaries | `layers` | `presentation → application → domain` |
| 6 | IAM/Audit domain has no infra imports | `forbidden` | Dependency inversion |
| 7 | Composition root is only cross-BC wiring | `independence` | Centralize wiring |

### 7.3 Pre-commit + CI

`import-linter` runs both as a pre-commit hook (immediate feedback) and in CI (`make arch-check`).

### 7.4 AGENTS.md update

Rule 11 is expanded into 4 rules (11–14) covering: BC boundaries, intra-BC layers, shared kernel discipline, and how to add a new BC.

---

## 8. Phased Migration Plan

**Strategy**: Phased migration with hard cut at each phase. After each phase:
- `make dev` runs
- `make test-all` is green
- `make arch-check` is green
- All endpoints respond (smoke test)
- Code is committed (no WIP carried over)

| Phase | Name | Est. Duration | Files Touched | Risk |
|---|---|---|---|---|
| 0 | Static Analysis Baseline | 1 day | ~3 (config) | Low |
| 1 | Shared Kernel + Platform | 2 days | ~30 (move) | Low |
| 2 | IAM Domain + Application | 3 days | ~50 | Medium |
| 3 | IAM Infrastructure + Presentation | 3 days | ~40 | Medium |
| 4 | Audit BC | 2 days | ~20 | Medium |
| 5 | Final Cleanup & Docs | 1 day | ~10 (docs) | Low |
| | **Total** | **12 days** | **~150 files** | |

### Phase 0 — Static Analysis Baseline

Add `import-linter` with contracts reflecting the **current** (layer-first) architecture as baseline. Add `make arch-check`. Add pre-commit hook. Snapshot current test count + coverage to `docs/superpowers/specs/refactor-baseline.md`. Create branch `refactor/bc-modular-monolith`.

**DoD**: arch-check green, tests green, baseline committed.

### Phase 1 — Shared Kernel + Platform

Extract `app/shared/` (base classes, ID value objects, application interfaces) and `app/platform/` (configs, web, DB managers, event bus impl, CLI) from existing code. Bulk update imports across the codebase. Update `import-linter` with "shared kernel dependency-free" contract. Migrate tests to `tests/shared/` and `tests/platform/`.

**DoD**: app runs, tests green, arch-check green. `app/core/` still contains domain + application (BCs not yet born).

### Phase 2 — IAM Domain + Application

Create `app/iam/domain/{user,role,permission,assignment}/` with the per-aggregate subfolder pattern. Create `app/iam/application/` with commands, queries, handlers, read models, and the new `IIamUnitOfWork` interface. Move all IAM domain + application code out of `app/core/` (hard cut — `app/core/` IAM code is deleted in this phase). Update **all** import paths across the codebase to point at `app/iam/` instead of `app/core/` — this includes the existing presentation and infrastructure files, which stay in their current locations but now import from `app/iam/`. Refactor assignment handler constructors: they no longer take `assignment_repository` / `event_bus` (the handler now receives `uow` via `handle()`); accordingly update the assignment DI providers in `app/presentation/dependencies/handlers.py` (which also stays in its current location until Phase 3). Delete IAM-related code from `app/core/` (Log stays). Update tests to `tests/iam/unit/`.

**DoD**: IAM domain + application exist at `app/iam/`. `app/core/` contains only Log-related code. Presentation + infrastructure files are still in their old locations but import from `app/iam/`. App runs, tests green, arch-check green.

### Phase 3 — IAM Infrastructure + Presentation

Create `app/iam/infrastructure/` (Postgres models, mappers, repositories, `PostgresIamUnitOfWork`) and `app/iam/presentation/` (API, dependencies, DTOs). Wire IAM router in `setup.py`. Delete old `app/presentation/api/v1/{user,role,permission}.py`, `app/presentation/dependencies/handlers.py`, `app/presentation/dependencies/repositories.py`, and related DTOs. Migrate tests to `tests/iam/{integration,e2e}/`.

**DoD**: `app/iam/` has all 4 layers. `app/core/` only contains Log. `app/presentation/` nearly empty. `make test-iam` green.

### Phase 4 — Audit BC

Create `app/audit/` with all 4 layers for `Log`. Create `AuditUserEventTranslator` in `app/audit/infrastructure/event_handlers/iam_event_handlers.py`. Wire cross-BC subscriptions in `setup.py`. Delete `app/core/` entirely. Delete old `app/infrastructure/event_handlers/user_event_handlers.py`. Migrate tests to `tests/audit/`. Add `tests/integration/test_cross_bc_event_flow.py`. Add full BC-isolation contracts to `import-linter`.

**DoD**: `app/core/` gone. `app/iam/`, `app/audit/`, `app/shared/`, `app/platform/` complete. Cross-BC event flow works end-to-end. Tests + arch-check green.

### Phase 5 — Final Cleanup & Docs

Rewrite `docs/architecture.md` with BC structure. Update `AGENTS.md` rules 11–14. Update `CLAUDE.md` architecture overview + key files. Add Makefile targets (`test-iam`, `test-audit`, `arch-check`). Verify final metrics (test count ≥ baseline, coverage ≥ baseline, endpoint count ≥ baseline). Tag release `v0.2.0-bc-modular`.

**DoD**: docs consistent with code, `make ci` green, release tagged.

---

## 9. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Breaking existing endpoints | After each phase: `curl` smoke test of every endpoint |
| Assignment handlers break due to constructor + signature change | Phase 2 changes handler constructors (removes `assignment_repository`/`event_bus` from `__init__`) and `handle()` signature (adds `uow` param). The DI providers that construct these handlers (currently in `app/presentation/dependencies/handlers.py`) are updated in the **same** Phase 2 commit. Phase 3 then moves the DI providers into `app/iam/presentation/dependencies/`. |
| DB session leak | `tests/iam/integration/test_iam_unit_of_work.py` verifies session close on both success and exception paths |
| Event publishing fails silently | `tests/integration/test_cross_bc_event_flow.py` verifies audit log was created after IAM commit |
| Missed import somewhere | `import-linter` + `pyright` enforce type-safe and contract-safe imports |
| Refactor interrupted mid-phase | Each phase is one commit → trivial revert |

---

## 10. Acceptance Criteria

The refactor is complete when **all** of the following hold:

1. `app/core/` no longer exists.
2. `app/iam/`, `app/audit/`, `app/shared/`, `app/platform/` each exist with the structure described in §3.
3. `app/infrastructure/setup.py` is the only file that imports from more than one BC.
4. `import-linter` contracts (§7.2) are all green.
5. All existing endpoints respond identically (verified by E2E tests).
6. Test count ≥ baseline (no tests dropped).
7. Coverage ≥ baseline.
8. `docs/architecture.md`, `AGENTS.md`, `CLAUDE.md` reflect the new structure.
9. Tag `v0.2.0-bc-modular` is created on main.

---

## 11. Appendix: Mapping Table (Current → Target)

| Current path | Target path |
|---|---|
| `app/core/domain/entities/base.py` | `app/shared/domain/base_entity.py` |
| `app/core/domain/events/base.py` | `app/shared/domain/base_event.py` |
| `app/core/domain/exceptions/base.py` | `app/shared/domain/base_exception.py` |
| `app/core/domain/exceptions/error_codes.py` | `app/shared/domain/error_codes.py` |
| `app/core/domain/exceptions/validation.py` | `app/shared/domain/validation.py` |
| `app/core/domain/value_objects/{user,role,permission,log}_id.py` | `app/shared/domain/ids/<same>.py` |
| `app/core/application/interfaces/{event,command,query}_bus.py` | `app/shared/application/interfaces/<same>.py` |
| `app/core/application/interfaces/unit_of_work.py` (base) | `app/shared/application/interfaces/unit_of_work.py` |
| `app/core/domain/aggregates/user.py` | `app/iam/domain/user/aggregate.py` |
| `app/core/domain/entities/user.py` | `app/iam/domain/user/entity.py` |
| `app/core/domain/value_objects/{email,username}.py` | `app/iam/domain/user/value_objects.py` |
| `app/core/domain/events/user_events.py` | `app/iam/domain/user/events.py` |
| `app/core/domain/specifications/user_specs.py` | `app/iam/domain/user/specifications.py` |
| `app/core/domain/exceptions/user.py` | `app/iam/domain/user/exceptions.py` |
| `app/core/domain/repositories/user.py` | `app/iam/domain/user/repository.py` |
| `app/core/domain/services/user_domain_service.py` | `app/iam/domain/user/domain_service.py` |
| (same pattern for `role`, `permission`) | `app/iam/domain/<aggregate>/...` |
| `app/core/application/commands/handlers/assignment_handlers.py` | `app/iam/application/handlers/assignment_handlers.py` |
| `app/core/application/commands/handlers/user_handlers.py` | `app/iam/application/handlers/user_handlers.py` |
| `app/core/domain/aggregates/log.py` | `app/audit/domain/log/aggregate.py` |
| `app/core/domain/value_objects/action.py` | `app/audit/domain/log/value_objects.py` |
| `app/infrastructure/web/` | `app/platform/web/` |
| `app/infrastructure/configs/` | `app/platform/configs/` |
| `app/infrastructure/messaging/event_bus.py` | `app/platform/messaging/event_bus.py` |
| `app/infrastructure/persistence/postgresql/database.py` | `app/platform/persistence/postgresql/database.py` |
| `app/infrastructure/persistence/mongodb/database.py` | `app/platform/persistence/mongodb/database.py` |
| `app/infrastructure/persistence/postgresql/models/` | `app/iam/infrastructure/persistence/postgresql/models/` |
| `app/infrastructure/persistence/postgresql/mappers/` | `app/iam/infrastructure/persistence/postgresql/mappers/` |
| `app/infrastructure/persistence/postgresql/repositories/` | `app/iam/infrastructure/persistence/postgresql/repositories/` |
| `app/infrastructure/persistence/postgresql/unit_of_work.py` | `app/iam/infrastructure/persistence/postgresql/unit_of_work.py` (as `PostgresIamUnitOfWork`) |
| `app/infrastructure/persistence/mongodb/` | `app/audit/infrastructure/persistence/mongodb/` |
| `app/infrastructure/messaging/password_hasher.py` | `app/iam/infrastructure/messaging/password_hasher.py` |
| `app/infrastructure/event_handlers/user_event_handlers.py` | `app/audit/infrastructure/event_handlers/iam_event_handlers.py` (as `AuditUserEventTranslator`) |
| `app/infrastructure/cli/` | `app/platform/cli/` |
| `app/presentation/api/v1/user.py` | `app/iam/presentation/api/user.py` |
| `app/presentation/api/v1/role.py` | `app/iam/presentation/api/role.py` |
| `app/presentation/api/v1/permission.py` | `app/iam/presentation/api/permission.py` |
| `app/presentation/api/v1/log.py` | `app/audit/presentation/api/log.py` |
| `app/presentation/dependencies/handlers.py` | split → `app/iam/presentation/dependencies/handlers.py` + `app/audit/presentation/dependencies/handlers.py` |
| `app/presentation/dependencies/repositories.py` | split → `app/iam/presentation/dependencies/repositories.py` + `app/audit/presentation/dependencies/repositories.py` |
| `app/presentation/dtos/{user,role,permission}.py` | `app/iam/presentation/dtos/<same>.py` |
| `app/presentation/dtos/log.py` | `app/audit/presentation/dtos/log.py` |
| `app/infrastructure/setup.py` | `app/infrastructure/setup.py` (stays as composition root) |
| `app/main.py` | `app/main.py` (stays, updated imports) |

---

## 12. Open Questions (none at spec time)

All clarifying questions resolved during brainstorming:
- BC decomposition: Option A (IAM + Audit + shared + platform) — chosen
- Refactor strategy: Phased migration with hard cut — chosen
- Internal BC structure: Pattern 1 (per-aggregate subfolder) — chosen
- Cross-BC isolation level: Level 2 (controlled sharing via shared kernel) — chosen
- BC folder name: `iam` — chosen
