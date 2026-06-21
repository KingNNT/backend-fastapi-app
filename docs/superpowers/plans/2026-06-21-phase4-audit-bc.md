# Phase 4: Audit BC (Log) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `app/audit/` Bounded Context containing all Log-related code currently in `app/core/`. Create `AuditUserEventTranslator` in audit (replacing the cross-BC `UserEventHandler` in infrastructure). Delete `app/core/` entirely. After this phase, the BC structure is complete: `iam/`, `audit/`, `shared/`, `platform/`, plus a thin composition root in `infrastructure/`.

**Architecture:** Mirror the IAM pattern from Phase 2/3: domain/application/infrastructure/presentation in the BC. The `AuditUserEventTranslator` lives in `app/audit/infrastructure/event_handlers/` and subscribes to IAM events via the composition root. The IAM BC does NOT import from audit — events flow through the event bus.

**Tech Stack:** Python 3.12, Poetry, Docker-first Makefile, import-linter, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-21-bc-modular-monolith-refactor-design.md` §3, §4.4, §8 Phase 4.

**Prerequisite:** Phase 3 complete (IAM BC fully extracted).

---

## File Structure

### Files to CREATE

```
app/audit/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── log/
│   │   ├── __init__.py
│   │   ├── aggregate.py       ← from app/core/domain/aggregates/log.py
│   │   ├── entity.py          ← from app/core/domain/entities/log.py
│   │   ├── value_objects.py   ← from app/core/domain/value_objects/action.py
│   │   ├── events.py          ← from app/core/domain/events/log_events.py
│   │   └── repository.py      ← from app/core/domain/repositories/log.py
│   └── shared/                # optional: cross-cutting audit types (none for now)
├── application/
│   ├── __init__.py
│   ├── commands/log/create_log.py
│   ├── queries/log/get_log.py
│   ├── queries/log/list_logs.py
│   ├── handlers/
│   │   ├── log_command_handlers.py
│   │   └── log_query_handlers.py
│   ├── read_models/log_read_model.py
│   └── interfaces/unit_of_work.py    ← IAuditUnitOfWork (new, MongoDB transaction wrapper)
├── infrastructure/
│   ├── __init__.py
│   ├── persistence/mongodb/
│   │   ├── __init__.py
│   │   ├── helpers.py        (if needed for Mongo connection)
│   │   ├── models/{base,log}.py
│   │   ├── mappers/log.py
│   │   └── repositories/{log_read,log_write}.py
│   ├── persistence/mongodb_unit_of_work.py    ← MongoAuditUnitOfWork (optional, since Log is single-doc)
│   └── event_handlers/
│       └── iam_event_translator.py    ← AuditUserEventTranslator (subscribes to IAM events)
└── presentation/
    ├── __init__.py
    ├── api/log.py
    ├── dependencies/
    │   ├── __init__.py
    │   ├── handlers.py        ← log handler factories + Dep aliases
    │   └── repositories.py    ← log repo factory
    └── dtos/log.py
```

### Files to DELETE (after moves + import updates)

- `app/core/` (entire directory)
- `app/infrastructure/persistence/mongodb/` (moved to audit/)
- `app/infrastructure/event_handlers/` (moved to audit/infrastructure/event_handlers/)

### Files NOT touched (staying in `app/infrastructure/`)

- `app/infrastructure/setup.py` — composition root (gets updated imports)

---

## Task 1: Create `app/audit/` directory structure

- [ ] **Step 1: Create all directories**

```bash
mkdir -p app/audit/domain/log
mkdir -p app/audit/application/commands/log
mkdir -p app/audit/application/queries/log
mkdir -p app/audit/application/{handlers,read_models,interfaces}
mkdir -p app/audit/infrastructure/persistence/mongodb/{models,mappers,repositories}
mkdir -p app/audit/infrastructure/event_handlers
mkdir -p app/audit/presentation/{api,dependencies,dtos}
```

- [ ] **Step 2: Create empty `__init__.py` files**

```bash
for d in app/audit app/audit/domain app/audit/domain/log app/audit/application app/audit/application/commands app/audit/application/commands/log app/audit/application/queries app/audit/application/queries/log app/audit/application/handlers app/audit/application/read_models app/audit/application/interfaces app/audit/infrastructure app/audit/infrastructure/persistence app/audit/infrastructure/persistence/mongodb app/audit/infrastructure/persistence/mongodb/models app/audit/infrastructure/persistence/mongodb/mappers app/audit/infrastructure/persistence/mongodb/repositories app/audit/infrastructure/event_handlers app/audit/presentation app/audit/presentation/api app/audit/presentation/dependencies app/audit/presentation/dtos; do
  touch "$d/__init__.py"
done
```

- [ ] **Step 3: Create top-level `app/audit/__init__.py`**

```python
"""Audit Bounded Context — immutable audit trail.

Subscribes to domain events from other BCs (currently iam/) and persists
audit log records in MongoDB.
"""
```

---

## Task 2: Move audit domain files

- [ ] **Step 1: Move aggregate, entity, events, repository, value_objects**

```bash
git mv app/core/domain/aggregates/log.py app/audit/domain/log/aggregate.py
git mv app/core/domain/entities/log.py app/audit/domain/log/entity.py
git mv app/core/domain/events/log_events.py app/audit/domain/log/events.py
git mv app/core/domain/repositories/log.py app/audit/domain/log/repository.py
git mv app/core/domain/value_objects/action.py app/audit/domain/log/value_objects.py
```

- [ ] **Step 2: Create barrel `app/audit/domain/log/__init__.py`**

```python
"""Log aggregate — audit trail domain layer."""

from app.audit.domain.log.aggregate import LogAggregate
from app.audit.domain.log.entity import Log
from app.audit.domain.log.events import LogCreated
from app.audit.domain.log.repository import (
    ILogReadRepository,
    ILogRepository,
    ILogWriteRepository,
)
from app.audit.domain.log.value_objects import Action

__all__ = [
    "LogAggregate",
    "Log",
    "Action",
    "LogCreated",
    "ILogRepository",
    "ILogReadRepository",
    "ILogWriteRepository",
]
```

(Adjust class names if they differ — check the actual file contents.)

- [ ] **Step 3: Create `app/audit/domain/__init__.py`**

```python
"""Audit domain layer — aggregate, entities, value objects, events."""
```

- [ ] **Step 4: Verify audit domain imports**

```bash
docker-compose exec -T python python -c "
from app.audit.domain.log import LogAggregate, Log, Action, LogCreated
print('audit domain OK')
"
```

---

## Task 3: Move audit application files

- [ ] **Step 1: Move command and query files**

```bash
git mv app/core/application/commands/log/create_log.py app/audit/application/commands/log/create_log.py
git mv app/core/application/queries/log/get_log.py app/audit/application/queries/log/get_log.py
git mv app/core/application/queries/log/list_logs.py app/audit/application/queries/log/list_logs.py
git mv app/core/application/commands/handlers/log_handlers.py app/audit/application/handlers/log_command_handlers.py
git mv app/core/application/queries/handlers/log_handlers.py app/audit/application/handlers/log_query_handlers.py
git mv app/core/application/read_models/log_read_model.py app/audit/application/read_models/log_read_model.py
```

- [ ] **Step 2: Update imports inside moved application files**

```bash
find app/audit/application -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain\.|from app.audit.domain.|g' \
  -e 's|from app\.core\.application\.interfaces|from app.audit.application.interfaces|g' \
  -e 's|from app\.core\.application\.read_models|from app.audit.application.read_models|g' \
  -e 's|from app\.shared\.domain\.|from app.shared.domain.|g' \
  {} +
```

- [ ] **Step 3: Create barrel `app/audit/application/handlers/__init__.py`**

```python
"""Audit application handlers."""

from app.audit.application.handlers.log_command_handlers import CreateLogHandler
from app.audit.application.handlers.log_query_handlers import (
    GetLogByIdHandler,
    ILogReadModelRepository,
    ListLogsByActionHandler,
    ListLogsByDateRangeHandler,
    ListLogsByUserHandler,
    ListLogsHandler,
)

__all__ = [
    "CreateLogHandler",
    "GetLogByIdHandler",
    "ListLogsHandler",
    "ListLogsByUserHandler",
    "ListLogsByActionHandler",
    "ListLogsByDateRangeHandler",
    "ILogReadModelRepository",
]
```

(Adjust based on actual exported names — check the original `app/core/application/queries/handlers/log_handlers.py`.)

- [ ] **Step 4: Create barrel `app/audit/application/commands/log/__init__.py`**

```python
"""Log commands."""

from app.audit.application.commands.log.create_log import CreateLogCommand

__all__ = ["CreateLogCommand"]
```

- [ ] **Step 5: Create barrel `app/audit/application/queries/log/__init__.py`**

```python
"""Log queries."""

from app.audit.application.queries.log.get_log import GetLogByIdQuery
from app.audit.application.queries.log.list_logs import (
    ListLogsActionQuery,
    ListLogsByDateRangeQuery,
    ListLogsByUserQuery,
    ListLogsQuery,
)

__all__ = [
    "GetLogByIdQuery",
    "ListLogsQuery",
    "ListLogsActionQuery",
    "ListLogsByDateRangeQuery",
    "ListLogsByUserQuery",
]
```

(Adjust based on actual exported names.)

- [ ] **Step 6: Create barrel `app/audit/application/__init__.py`**

```python
"""Audit application layer — CQRS commands, queries, handlers."""
```

- [ ] **Step 7: Verify audit application imports**

```bash
docker-compose exec -T python python -c "
from app.audit.application.commands.log import CreateLogCommand
from app.audit.application.queries.log import GetLogByIdQuery
from app.audit.application.handlers import CreateLogHandler
print('audit application OK')
"
```

---

## Task 4: Move audit infrastructure (MongoDB models, mappers, repos)

- [ ] **Step 1: Move MongoDB infrastructure files**

```bash
git mv app/infrastructure/persistence/mongodb/models/base.py app/audit/infrastructure/persistence/mongodb/models/base.py
git mv app/infrastructure/persistence/mongodb/models/log.py app/audit/infrastructure/persistence/mongodb/models/log.py
git mv app/infrastructure/persistence/mongodb/mappers/log.py app/audit/infrastructure/persistence/mongodb/mappers/log.py
git mv app/infrastructure/persistence/mongodb/repositories/log_read.py app/audit/infrastructure/persistence/mongodb/repositories/log_read.py
git mv app/infrastructure/persistence/mongodb/repositories/log_write.py app/audit/infrastructure/persistence/mongodb/repositories/log_write.py
```

- [ ] **Step 2: Update imports inside moved infrastructure files**

```bash
find app/audit/infrastructure -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain\.|from app.audit.domain.|g' \
  -e 's|from app\.core\.application\.|from app.audit.application.|g' \
  -e 's|from app\.infrastructure\.persistence\.mongodb\.models|from app.audit.infrastructure.persistence.mongodb.models|g' \
  -e 's|from app\.infrastructure\.persistence\.mongodb\.repositories|from app.audit.infrastructure.persistence.mongodb.repositories|g' \
  {} +
```

- [ ] **Step 3: Create barrel `app/audit/infrastructure/persistence/mongodb/models/__init__.py`**

(Inspect `models/base.py` and `models/log.py` for the model class names, then add:)

```python
"""MongoDB persistence models."""

from app.audit.infrastructure.persistence.mongodb.models.base import BaseDocument
from app.audit.infrastructure.persistence.mongodb.models.log import LogModel

__all__ = ["BaseDocument", "LogModel"]
```

(Adjust names based on actual files.)

- [ ] **Step 4: Create barrel `app/audit/infrastructure/persistence/mongodb/repositories/__init__.py`**

```python
"""MongoDB repository implementations."""

from app.audit.infrastructure.persistence.mongodb.repositories.log_read import (
    MongoLogReadModelRepository,
    MongoLogReadRepository,
)
from app.audit.infrastructure.persistence.mongodb.repositories.log_write import (
    MongoLogWriteRepository,
)

__all__ = [
    "MongoLogReadRepository",
    "MongoLogReadModelRepository",
    "MongoLogWriteRepository",
]
```

(Adjust based on actual file contents.)

- [ ] **Step 5: Create barrel `app/audit/infrastructure/persistence/mongodb/__init__.py`**

```python
"""Audit MongoDB persistence layer."""
```

- [ ] **Step 6: Create barrel `app/audit/infrastructure/__init__.py`**

```python
"""Audit infrastructure layer."""
```

- [ ] **Step 7: Verify audit infrastructure imports**

```bash
docker-compose exec -T python python -c "
from app.audit.infrastructure.persistence.mongodb.models import LogModel
from app.audit.infrastructure.persistence.mongodb.repositories import MongoLogWriteRepository
print('audit infrastructure OK')
"
```

---

## Task 5: Create AuditUserEventTranslator

The cross-BC event handler — replaces the old `UserEventHandler` in `app/infrastructure/event_handlers/`. Now lives in `app/audit/infrastructure/event_handlers/` and subscribes to IAM events.

- [ ] **Step 1: Move `user_event_handlers.py` → `iam_event_translator.py`**

```bash
git mv app/infrastructure/event_handlers/user_event_handlers.py app/audit/infrastructure/event_handlers/iam_event_translator.py
```

- [ ] **Step 2: Rename class and update imports**

In `app/audit/infrastructure/event_handlers/iam_event_translator.py`:
- Replace `class UserEventHandler:` → `class AuditUserEventTranslator:`
- Update imports:
  - `from app.core.application.commands.handlers.log_handlers import CreateLogHandler` → `from app.audit.application.handlers import CreateLogHandler`
  - `from app.core.application.commands.log.create_log import CreateLogCommand` → `from app.audit.application.commands.log import CreateLogCommand`
  - `from app.iam.domain.user.events import (...)` → already correct (IAM events are cross-BC contracts)

- [ ] **Step 3: Create barrel `app/audit/infrastructure/event_handlers/__init__.py`**

```python
"""Audit event handlers — translate cross-BC events into audit log commands."""

from app.audit.infrastructure.event_handlers.iam_event_translator import (
    AuditUserEventTranslator,
)

__all__ = ["AuditUserEventTranslator"]
```

- [ ] **Step 4: Verify translator imports**

```bash
docker-compose exec -T python python -c "
from app.audit.infrastructure.event_handlers import AuditUserEventTranslator
print('translator OK')
"
```

---

## Task 6: Create audit presentation (api, dtos, deps, router)

- [ ] **Step 1: Move API router**

```bash
git mv app/presentation/api/v1/log.py app/audit/presentation/api/log.py
```

- [ ] **Step 2: Update imports inside log router**

```bash
find app/audit/presentation/api -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.application\.commands\.handlers\.log_handlers import|from app.audit.application.handlers import|g' \
  -e 's|from app\.core\.application\.queries\.handlers\.log_handlers import|from app.audit.application.handlers import|g' \
  -e 's|from app\.core\.application\.commands\.log import|from app.audit.application.commands.log import|g' \
  -e 's|from app\.core\.application\.queries\.log import|from app.audit.application.queries.log import|g' \
  -e 's|from app\.presentation\.dependencies import|from app.audit.presentation.dependencies import|g' \
  {} +
```

(If any patterns don't match, manually inspect with `rg`.)

- [ ] **Step 3: Move DTOs**

```bash
git mv app/presentation/dtos/log.py app/audit/presentation/dtos/log.py
```

- [ ] **Step 4: Update DTO imports**

```bash
find app/audit/presentation/dtos -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain\.|from app.audit.domain.|g' \
  -e 's|from app\.shared\.domain\.|from app.shared.domain.|g' \
  -e 's|from app\.platform\.web\.response_dtos|from app.platform.web.response_dtos|g' \
  {} +
```

- [ ] **Step 5: Move presentation dependencies (Log-specific files)**

The Log-specific handlers and repository deps were created in Phase 3 in `app/presentation/dependencies/`. They need to be moved:

```bash
git mv app/presentation/dependencies/handlers.py app/audit/presentation/dependencies/handlers.py
```

But `app/presentation/dependencies/repositories.py` also has Log repo factories. Move it:

```bash
git mv app/presentation/dependencies/repositories.py app/audit/presentation/dependencies/repositories.py
```

- [ ] **Step 6: Update deps imports**

```bash
find app/audit/presentation/dependencies -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.application\.queries\.handlers\.log_handlers import|from app.audit.application.handlers import|g' \
  -e 's|from app\.core\.application\.commands\.handlers\.log_handlers import|from app.audit.application.handlers import|g' \
  -e 's|from app\.core\.domain\.repositories\.log import|from app.audit.domain.log.repository import|g' \
  -e 's|from app\.platform\.messaging\.services|from app.platform.messaging.services|g' \
  {} +
```

- [ ] **Step 7: Create barrel `app/audit/presentation/dependencies/__init__.py`**

```python
"""Audit presentation dependency providers."""

from app.audit.presentation.dependencies.handlers import (
    CreateLogHandlerDep,
    GetLogByIdHandlerDep,
    ListLogsByUserHandlerDep,
    ListLogsHandlerDep,
    get_create_log_handler,
    get_list_logs_by_user_handler,
    get_list_logs_handler,
    get_log_by_id_handler,
)
from app.audit.presentation.dependencies.repositories import (
    PostgresSessionDep,
    get_log_read_model_repository,
    get_log_repository,
    set_log_read_model_repository,
    set_log_repository,
)

__all__ = [
    "get_log_repository",
    "get_log_read_model_repository",
    "set_log_repository",
    "set_log_read_model_repository",
    "PostgresSessionDep",
    "get_create_log_handler",
    "get_log_by_id_handler",
    "get_list_logs_handler",
    "get_list_logs_by_user_handler",
    "CreateLogHandlerDep",
    "GetLogByIdHandlerDep",
    "ListLogsHandlerDep",
    "ListLogsByUserHandlerDep",
]
```

(Adjust based on actual exported names.)

- [ ] **Step 8: Create `app/audit/presentation/api/__init__.py` (router aggregator)**

```python
"""Audit API router aggregator."""

from fastapi import APIRouter

from app.audit.presentation.api import log

router = APIRouter()
router.include_router(log.router)
```

- [ ] **Step 9: Create barrel `app/audit/presentation/__init__.py`**

```python
"""Audit presentation layer."""
```

- [ ] **Step 10: Verify audit presentation imports**

```bash
docker-compose exec -T python python -c "
from app.audit.presentation.api import router as audit_router
from app.audit.presentation.dependencies import CreateLogHandlerDep
print('audit presentation OK')
"
```

---

## Task 7: Update `app/main.py` to include audit router

- [ ] **Step 1: Update main.py**

```python
# In app/main.py, add the audit router include
from app.audit.presentation.api import router as audit_router

# ...

app.include_router(iam_router, prefix="/v1")
app.include_router(audit_router, prefix="/v1")  # /v1/logs/
```

---

## Task 8: Update `app/infrastructure/setup.py` for cross-BC wiring

The composition root needs to subscribe the AuditUserEventTranslator to IAM events.

- [ ] **Step 1: Update setup.py imports**

```python
# OLD:
from app.infrastructure.event_handlers import UserEventHandler

# NEW:
from app.audit.infrastructure.event_handlers import AuditUserEventTranslator
```

- [ ] **Step 2: Update setup_app_services()**

In the section that creates event handlers:

```python
# OLD:
user_event_handler = UserEventHandler(create_log_handler=log_handler)

# NEW:
audit_user_translator = AuditUserEventTranslator(create_log_handler=log_handler)
```

Update `event_bus.subscribe()` calls:

```python
# OLD:
event_bus.subscribe(UserCreated, user_event_handler.on_user_created)
event_bus.subscribe(UserUpdated, user_event_handler.on_user_updated)
event_bus.subscribe(UserDeleted, user_event_handler.on_user_deleted)
event_bus.subscribe(UserDeactivated, user_event_handler.on_user_deactivated)
event_bus.subscribe(UserActivated, user_event_handler.on_user_activated)

# NEW:
event_bus.subscribe(UserCreated, audit_user_translator.on_user_created)
event_bus.subscribe(UserUpdated, audit_user_translator.on_user_updated)
event_bus.subscribe(UserDeleted, audit_user_translator.on_user_deleted)
event_bus.subscribe(UserDeactivated, audit_user_translator.on_user_deactivated)
event_bus.subscribe(UserActivated, audit_user_translator.on_user_activated)
```

- [ ] **Step 3: Verify setup.py**

```bash
docker-compose exec -T python python -c "from app.infrastructure.setup import setup_app_services; print('setup OK')"
```

---

## Task 9: Delete `app/core/` and clean up old paths

- [ ] **Step 1: Delete app/core/**

```bash
rm -rf app/core/
echo "core deleted"
```

- [ ] **Step 2: Delete old infrastructure paths**

```bash
rm -rf app/infrastructure/persistence/mongodb/
rm -rf app/infrastructure/event_handlers/
echo "old infrastructure paths deleted"
```

- [ ] **Step 3: Update old presentation deps that referenced moved files**

`app/presentation/dependencies/__init__.py` was updated in Phase 3. After Phase 4:
- The Log handlers/repositories moved to `app/audit/presentation/dependencies/`
- The presentation layer only has the `system.py` (already there)

Need to update `app/presentation/dependencies/__init__.py` to:
- Only re-export the system route (it's in `app/presentation/api/system.py`, doesn't need DI)

Actually, looking at current state: `app/presentation/dependencies/__init__.py` exports Log handler deps. After moving, those imports won't exist. Let me check if anything still imports from `app.presentation.dependencies`.

```bash
rg "from app\.presentation\.dependencies" app/ tests/ | head -10
```

If only test files reference it, update those. Otherwise, keep the imports with re-exports from the new audit location (for backward compat).

- [ ] **Step 4: Update all remaining imports across codebase**

```bash
find app tests -name "*.py" -not -path "app/audit/*" -not -path "app/iam/*" -not -path "app/shared/*" -not -path "app/platform/*" -exec sed -i '' \
  -e 's|from app\.core\.application\.commands\.handlers\.log_handlers import|from app.audit.application.handlers import|g' \
  -e 's|from app\.core\.application\.commands\.log import|from app.audit.application.commands.log import|g' \
  -e 's|from app\.core\.application\.queries\.handlers\.log_handlers import|from app.audit.application.handlers import|g' \
  -e 's|from app\.core\.application\.queries\.log import|from app.audit.application.queries.log import|g' \
  -e 's|from app\.core\.application\.read_models\.log_read_model import|from app.audit.application.read_models.log_read_model import|g' \
  -e 's|from app\.core\.domain\.aggregates\.log import|from app.audit.domain.log.aggregate import|g' \
  -e 's|from app\.core\.domain\.entities\.log import|from app.audit.domain.log.entity import|g' \
  -e 's|from app\.core\.domain\.events\.log_events import|from app.audit.domain.log.events import|g' \
  -e 's|from app\.core\.domain\.repositories\.log import|from app.audit.domain.log.repository import|g' \
  -e 's|from app\.core\.domain\.value_objects\.action import|from app.audit.domain.log.value_objects import|g' \
  -e 's|from app\.infrastructure\.event_handlers\.user_event_handlers|from app.audit.infrastructure.event_handlers.iam_event_translator|g' \
  -e 's|from app\.infrastructure\.event_handlers import|from app.audit.infrastructure.event_handlers import|g' \
  -e 's|from app\.infrastructure\.persistence\.mongodb\.models|from app.audit.infrastructure.persistence.mongodb.models|g' \
  -e 's|from app\.infrastructure\.persistence\.mongodb\.repositories|from app.audit.infrastructure.persistence.mongodb.repositories|g' \
  -e 's|from app\.infrastructure\.persistence\.mongodb\.mappers|from app.audit.infrastructure.persistence.mongodb.mappers|g' \
  -e 's|from app\.presentation\.api\.v1\.log|from app.audit.presentation.api.log|g' \
  -e 's|from app\.presentation\.dtos\.log import|from app.audit.presentation.dtos.log import|g' \
  {} +
```

- [ ] **Step 5: Verify no stale references**

```bash
rg "app\.core\." app/ tests/ -l 2>/dev/null | grep -v "app/core/" | wc -l
echo "---"
rg "app\.infrastructure\.event_handlers" app/ tests/ -l 2>/dev/null | grep -v "app/audit/"
echo "---"
rg "app\.infrastructure\.persistence\.mongodb" app/ tests/ -l 2>/dev/null | grep -v "app/audit/"
```

All should be 0.

---

## Task 10: Update tests

- [ ] **Step 1: Move audit-related tests**

The current `tests/integration/` and `tests/e2e/` have Log-related tests. They should move to `tests/audit/`:

```bash
mkdir -p tests/audit/{unit,integration,e2e}
git mv tests/integration/event_handlers/test_user_events.py tests/audit/integration/
git mv tests/integration/mongodb/test_log_repository.py tests/audit/integration/
```

(E2E Log tests don't currently exist — the e2e/test_user_api.py is for IAM only.)

- [ ] **Step 2: Update test imports**

```bash
find tests/audit -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain|from app.audit.domain|g' \
  -e 's|from app\.core\.application|from app.audit.application|g' \
  -e 's|from app\.infrastructure\.persistence\.mongodb|from app.audit.infrastructure.persistence.mongodb|g' \
  -e 's|from app\.infrastructure\.event_handlers|from app.audit.infrastructure.event_handlers|g' \
  -e 's|from app\.shared\.domain|from app.shared.domain|g' \
  -e 's|from app\.platform\.messaging|from app.platform.messaging|g' \
  {} +
```

- [ ] **Step 3: Update unit test imports**

`tests/unit/domain/test_aggregates.py` imports Log aggregate:
```bash
rg "LogAggregate\|from app\.core\.domain\.aggregates\.log" tests/unit/ | head -5
```

Update these to `from app.audit.domain.log.aggregate import LogAggregate`.

- [ ] **Step 4: Verify all tests pass**

```bash
make test-all
```

Expected: 145 tests pass.

---

## Task 11: Update import-linter contracts

- [ ] **Step 1: Update IAM contract**

The IAM contract `name = "IAM does not import from core (Log BC)"` is now obsolete (Log moved to audit). Change to "IAM does not import from audit BC":

```toml
[[tool.importlinter.contracts]]
name = "IAM does not import from audit BC"
type = "forbidden"
source_modules = ["app.iam"]
forbidden_modules = ["app.audit"]
```

- [ ] **Step 2: Add audit contracts**

```toml
[[tool.importlinter.contracts]]
name = "Audit layer boundaries"
type = "layers"
layers = [
    "app.audit.presentation",
    "app.audit.application",
    "app.audit.domain",
]

[[tool.importlinter.contracts]]
name = "Audit domain has no infrastructure or framework imports"
type = "forbidden"
source_modules = ["app.audit.domain"]
forbidden_modules = [
    "app.audit.infrastructure",
    "app.infrastructure",
    "app.platform",
    "app.presentation",
    "fastapi",
    "beanie",
    "motor",
    "pymongo",
]

[[tool.importlinter.contracts]]
name = "Audit does not import from iam BC"
type = "forbidden"
source_modules = ["app.audit"]
forbidden_modules = ["app.iam"]
```

NOTE: The last contract `Audit does not import from iam BC` will fail because `iam_event_translator.py` imports IAM events! This is the legitimate cross-BC exception. Add `ignore_imports` for that specific case:

```toml
ignore_imports = [
    "app.audit.infrastructure.event_handlers.iam_event_translator -> app.iam.domain.user.events",
]
```

- [ ] **Step 3: Run arch-check**

```bash
make arch-check
```

Expected: all contracts KEPT (count grows to ~12-13).

---

## Task 12: Commit Phase 4

- [ ] **Step 1: Final verification**

```bash
make format-check
make lint
make arch-check
make test-all
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "refactor: create Audit Bounded Context (Log), delete app/core/

Phase 4 of BC modular monolith refactor:

Audit BC structure (app/audit/):
- domain/log/ - aggregate, entity, value_objects, events, repository
- application/{commands,queries,handlers,read_models,interfaces}/
- infrastructure/persistence/mongodb/ - models, mappers, repositories
- infrastructure/event_handlers/iam_event_translator.py (cross-BC glue)
- presentation/{api,dependencies,dtos}/

Cross-BC event flow:
- AuditUserEventTranslator (in audit/) subscribes to IAM events
- Translated to CreateLogCommand -> persisted to MongoDB
- IAM BC never imports audit; events flow through event bus

Cleanup:
- app/core/ deleted entirely (was holding the temporary Log code)
- app/infrastructure/persistence/mongodb/ moved to app/audit/
- app/infrastructure/event_handlers/ moved to app/audit/
- All imports across codebase updated
- All 145 tests pass (98 unit + 30 integration + 17 e2e)
- 12/12 architectural contracts kept (BC isolation enforced)"
```

---

## Task 13: Phase 4 DoD verification

- [ ] **Step 1: `app/core/` is gone**

```bash
test ! -d app/core && echo "core deleted"
```

- [ ] **Step 2: `app/audit/` exists with all layers**

```bash
ls app/audit/
echo "---"
ls app/audit/domain/log/
echo "---"
ls app/audit/application/
echo "---"
ls app/audit/infrastructure/
echo "---"
ls app/audit/presentation/
```

- [ ] **Step 3: Audit router included in main app**

```bash
docker-compose exec -T python python -c "
from app.main import app
audit_routes = [r for r in app.routes if hasattr(r, 'methods') and '/v1/logs' in str(r.path)]
print('audit routes:', len(audit_routes))
for r in audit_routes:
    print(' ', list(r.methods), r.path)
"
```

- [ ] **Step 4: All 145 tests pass**

```bash
make test-all
```

- [ ] **Step 5: Arch-check 12+ KEPT**

```bash
make arch-check
```
