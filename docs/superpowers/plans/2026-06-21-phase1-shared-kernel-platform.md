# Phase 1: Shared Kernel + Platform Extraction — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract `app/shared/` (base classes, ID value objects, bus interfaces) and `app/platform/` (configs, web, DB managers, event bus impl, CLI) from the existing layer-first code. After this phase, `app/core/` still contains domain + application code for aggregates, but all cross-cutting infrastructure and shared kernel code lives in its own top-level packages.

**Architecture:** Physical file moves + bulk import updates. No behavioral changes. The existing `IUnitOfWork` (with repo attributes) stays in `app/core/application/interfaces/` for now — it will be split into base + IAM-specific in Phase 2. Only the 3 bus interfaces (event/command/query) move to `shared/`.

**Tech Stack:** Python 3.12, Poetry, Docker-first Makefile, import-linter, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-21-bc-modular-monolith-refactor-design.md` §3 (folder structure), §8 Phase 1.

**Prerequisite:** Phase 0 complete (import-linter + baseline metrics in place).

---

## File Structure

### Files to CREATE (new locations)

| New path | Sourced from |
|---|---|
| `app/shared/__init__.py` | new |
| `app/shared/domain/__init__.py` | new (barrel export) |
| `app/shared/domain/base_entity.py` | `app/core/domain/entities/base.py` |
| `app/shared/domain/base_event.py` | `app/core/domain/events/base.py` |
| `app/shared/domain/base_exception.py` | `app/core/domain/exceptions/base.py` |
| `app/shared/domain/error_codes.py` | `app/core/domain/exceptions/error_codes.py` |
| `app/shared/domain/validation.py` | `app/core/domain/exceptions/validation.py` |
| `app/shared/domain/ids/__init__.py` | new (barrel export) |
| `app/shared/domain/ids/user_id.py` | `app/core/domain/value_objects/user_id.py` |
| `app/shared/domain/ids/role_id.py` | `app/core/domain/value_objects/role_id.py` |
| `app/shared/domain/ids/permission_id.py` | `app/core/domain/value_objects/permission_id.py` |
| `app/shared/domain/ids/log_id.py` | `app/core/domain/value_objects/log_id.py` |
| `app/shared/application/__init__.py` | new |
| `app/shared/application/interfaces/__init__.py` | new (barrel export) |
| `app/shared/application/interfaces/event_bus.py` | `app/core/application/interfaces/event_bus.py` |
| `app/shared/application/interfaces/command_bus.py` | `app/core/application/interfaces/command_bus.py` |
| `app/shared/application/interfaces/query_bus.py` | `app/core/application/interfaces/query_bus.py` |
| `app/platform/__init__.py` | new |
| `app/platform/configs/__init__.py` | `app/infrastructure/configs/__init__.py` |
| `app/platform/configs/app.py` | `app/infrastructure/configs/app.py` |
| `app/platform/configs/logging.py` | `app/infrastructure/configs/logging.py` |
| `app/platform/configs/version.py` | `app/infrastructure/configs/version.py` |
| `app/platform/web/__init__.py` | `app/infrastructure/web/__init__.py` |
| `app/platform/web/exception_handlers.py` | `app/infrastructure/web/exception_handlers.py` |
| `app/platform/web/middleware.py` | `app/infrastructure/web/middleware.py` |
| `app/platform/web/response.py` | `app/infrastructure/web/response.py` |
| `app/platform/messaging/__init__.py` | new |
| `app/platform/messaging/event_bus.py` | `app/infrastructure/messaging/event_bus.py` |
| `app/platform/persistence/__init__.py` | new |
| `app/platform/persistence/postgresql/__init__.py` | new |
| `app/platform/persistence/postgresql/database.py` | `app/infrastructure/persistence/postgresql/database.py` |
| `app/platform/persistence/mongodb/__init__.py` | new |
| `app/platform/persistence/mongodb/database.py` | `app/infrastructure/persistence/mongodb/database.py` |
| `app/platform/cli/...` | `app/infrastructure/cli/...` (whole tree) |

### Files to DELETE (after moves + import updates)

All the "sourced from" paths above are deleted after their content is moved and all imports updated.

### Files to MODIFY (barrel exports + import paths)

- `app/core/domain/exceptions/__init__.py` — remove base/error_codes/validation re-exports
- `app/core/domain/entities/__init__.py` — remove BaseEntity re-export
- `app/core/domain/events/__init__.py` — remove BaseDomainEvent re-export
- `app/core/domain/value_objects/__init__.py` — remove ID re-exports
- `app/core/application/interfaces/__init__.py` — remove bus re-exports
- `app/infrastructure/messaging/__init__.py` — update (remove event_bus)
- `app/main.py` — update imports for configs/web
- `app/infrastructure/setup.py` — update imports for configs/messaging/persistence
- ~50+ files that import from the moved modules

### Files NOT touched in Phase 1

- `app/core/application/interfaces/unit_of_work.py` — stays as-is (Phase 2 will split it)
- `app/core/domain/exceptions/{user,role,permission}.py` — stay (Phase 2 moves them to iam/)
- `app/core/domain/entities/{user,role,permission,log}.py` — stay
- `app/core/domain/aggregates/` — stays
- `app/infrastructure/persistence/postgresql/{models,mappers,repositories,unit_of_work,migrations,seeds,helpers}` — stay
- `app/infrastructure/persistence/mongodb/{models,mappers,repositories}` — stay
- `app/infrastructure/messaging/password_hasher.py` — stays
- `app/infrastructure/event_handlers/` — stays
- `app/presentation/` — stays
- `app/infrastructure/setup.py` — stays (but imports updated)

---

## Task 1: Create `app/shared/domain/` — base classes + error codes + IDs

**Files:**
- Create: `app/shared/__init__.py`, `app/shared/domain/__init__.py`, `app/shared/domain/ids/__init__.py`
- Create: `app/shared/domain/error_codes.py` (copy of `app/core/domain/exceptions/error_codes.py`)
- Create: `app/shared/domain/base_exception.py` (copy of `app/core/domain/exceptions/base.py`, update internal import)
- Create: `app/shared/domain/validation.py` (copy of `app/core/domain/exceptions/validation.py`, update internal imports)
- Create: `app/shared/domain/base_entity.py` (copy of `app/core/domain/entities/base.py`)
- Create: `app/shared/domain/base_event.py` (copy of `app/core/domain/events/base.py`)
- Create: `app/shared/domain/ids/{user_id,role_id,permission_id,log_id}.py` (copies)

- [ ] **Step 1: Create directory structure + __init__.py files**

```bash
mkdir -p app/shared/domain/ids
```

Create `app/shared/__init__.py`:
```python
"""Shared Kernel — cross-Bounded-Context contracts and base types.

This package contains ONLY:
- Base classes (BaseEntity, BaseDomainEvent, DomainException)
- ID value objects (UserId, RoleId, PermissionId, LogId)
- Application interfaces (IEventBus, ICommandBus, IQueryBus)

It MUST NOT import from any Bounded Context (iam, audit) or platform code.
"""
```

Create `app/shared/domain/__init__.py`:
```python
"""Shared domain primitives — base classes, exceptions, IDs."""

from app.shared.domain.base_entity import BaseEntity, utc_now
from app.shared.domain.base_event import BaseDomainEvent
from app.shared.domain.base_exception import (
    DomainException,
    EntityAlreadyExists,
    EntityNotFound,
)
from app.shared.domain.error_codes import ErrorCode
from app.shared.domain.validation import BusinessRuleViolation, ValidationError

__all__ = [
    "BaseEntity",
    "utc_now",
    "BaseDomainEvent",
    "DomainException",
    "EntityNotFound",
    "EntityAlreadyExists",
    "ErrorCode",
    "ValidationError",
    "BusinessRuleViolation",
]
```

Create `app/shared/domain/ids/__init__.py`:
```python
"""Shared ID value objects — cross-BC identity contracts."""

from app.shared.domain.ids.log_id import LogId
from app.shared.domain.ids.permission_id import PermissionId
from app.shared.domain.ids.role_id import RoleId
from app.shared.domain.ids.user_id import UserId

__all__ = ["UserId", "RoleId", "PermissionId", "LogId"]
```

- [ ] **Step 2: Copy `error_codes.py` (no import changes needed)**

```bash
cp app/core/domain/exceptions/error_codes.py app/shared/domain/error_codes.py
```

- [ ] **Step 3: Copy `base_exception.py` — update internal import**

```bash
cp app/core/domain/exceptions/base.py app/shared/domain/base_exception.py
```

Then edit `app/shared/domain/base_exception.py`: change the import line:
```python
# OLD:
from app.core.domain.exceptions.error_codes import ErrorCode
# NEW:
from app.shared.domain.error_codes import ErrorCode
```

- [ ] **Step 4: Copy `validation.py` — update internal imports**

```bash
cp app/core/domain/exceptions/validation.py app/shared/domain/validation.py
```

Then edit `app/shared/domain/validation.py`: change imports:
```python
# OLD:
from app.core.domain.exceptions.base import DomainException
from app.core.domain.exceptions.error_codes import ErrorCode
# NEW:
from app.shared.domain.base_exception import DomainException
from app.shared.domain.error_codes import ErrorCode
```

- [ ] **Step 5: Copy `base_entity.py` (no import changes needed — only imports datetime/uuid)**

```bash
cp app/core/domain/entities/base.py app/shared/domain/base_entity.py
```

- [ ] **Step 6: Copy `base_event.py`**

First read the source to see its imports:
```bash
cat app/core/domain/events/base.py
```

Copy it, and update any internal imports to point to `app.shared.domain.*`:
```bash
cp app/core/domain/events/base.py app/shared/domain/base_event.py
```

Check and update imports inside the file if it references `app.core.domain.*`.

- [ ] **Step 7: Copy the 4 ID value objects**

```bash
cp app/core/domain/value_objects/user_id.py app/shared/domain/ids/user_id.py
cp app/core/domain/value_objects/role_id.py app/shared/domain/ids/role_id.py
cp app/core/domain/value_objects/permission_id.py app/shared/domain/ids/permission_id.py
cp app/core/domain/value_objects/log_id.py app/shared/domain/ids/log_id.py
```

These files have no internal imports (only stdlib `uuid`), so no changes needed.

- [ ] **Step 8: Verify the shared/domain package imports cleanly**

```bash
docker-compose exec -T python python -c "from app.shared.domain import BaseEntity, DomainException, ErrorCode; from app.shared.domain.ids import UserId, RoleId; print('OK')"
```

Expected: `OK`

- [ ] **Step 9: Do NOT delete old files yet — do that in Task 4 after all imports are updated**

---

## Task 2: Create `app/shared/application/interfaces/` — bus interfaces

**Files:**
- Create: `app/shared/application/__init__.py`, `app/shared/application/interfaces/__init__.py`
- Create: `app/shared/application/interfaces/event_bus.py` (copy)
- Create: `app/shared/application/interfaces/command_bus.py` (copy)
- Create: `app/shared/application/interfaces/query_bus.py` (copy)

- [ ] **Step 1: Create directories + __init__.py files**

```bash
mkdir -p app/shared/application/interfaces
```

Create `app/shared/application/__init__.py`:
```python
"""Shared application interfaces — cross-BC contracts."""
```

Create `app/shared/application/interfaces/__init__.py`:
```python
"""Shared application interfaces — buses and contracts.

Note: IUnitOfWork stays in app/core/application/interfaces/ for now.
It will be split into base (shared) + IAM-specific in Phase 2.
"""

from app.shared.application.interfaces.command_bus import (
    ICommand,
    ICommandBus,
    ICommandHandler,
)
from app.shared.application.interfaces.event_bus import IEventBus
from app.shared.application.interfaces.query_bus import (
    IQuery,
    IQueryBus,
    IQueryHandler,
)

__all__ = [
    "IEventBus",
    "ICommand",
    "ICommandHandler",
    "ICommandBus",
    "IQuery",
    "IQueryHandler",
    "IQueryBus",
]
```

- [ ] **Step 2: Copy the 3 bus interface files and update imports**

```bash
cp app/core/application/interfaces/event_bus.py app/shared/application/interfaces/event_bus.py
cp app/core/application/interfaces/command_bus.py app/shared/application/interfaces/command_bus.py
cp app/core/application/interfaces/query_bus.py app/shared/application/interfaces/query_bus.py
```

Check `event_bus.py` for internal imports — if it imports `BaseDomainEvent` from `app.core.domain.events.base`, update to `app.shared.domain.base_event`. The other two only use stdlib `typing`.

- [ ] **Step 3: Verify the shared/application package imports cleanly**

```bash
docker-compose exec -T python python -c "from app.shared.application.interfaces import IEventBus, ICommandBus, IQueryBus; print('OK')"
```

Expected: `OK`

---

## Task 3: Create `app/platform/configs/`

**Files:**
- Create: `app/platform/__init__.py`
- Create: `app/platform/configs/__init__.py` (update internal imports)
- Create: `app/platform/configs/app.py` (copy)
- Create: `app/platform/configs/logging.py` (copy)
- Create: `app/platform/configs/version.py` (copy)

- [ ] **Step 1: Create directory structure + __init__.py**

```bash
mkdir -p app/platform
```

Create `app/platform/__init__.py`:
```python
"""Platform — cross-cutting infrastructure shared across all Bounded Contexts.

Contains: configs, web middleware/handlers, DB connection managers, event bus
implementation, CLI tools. This package MUST NOT import from any BC (iam, audit).
"""
```

- [ ] **Step 2: Copy configs and update internal imports**

```bash
cp -r app/infrastructure/configs app/platform/configs
```

Edit `app/platform/configs/__init__.py`: change:
```python
# OLD:
from app.infrastructure.configs.app import get_app_config
from app.infrastructure.configs.logging import get_log_config
from app.infrastructure.configs.version import get_app_version, get_version_info
# NEW:
from app.platform.configs.app import get_app_config
from app.platform.configs.logging import get_log_config
from app.platform.configs.version import get_app_version, get_version_info
```

Check the 3 config files for any internal imports — they likely only import from pydantic-settings, so no changes needed.

- [ ] **Step 3: Verify imports**

```bash
docker-compose exec -T python python -c "from app.platform.configs import get_app_config; print('OK')"
```

---

## Task 4: Move `app/platform/web/` and `app/platform/messaging/`

**Files:**
- Create: `app/platform/web/__init__.py` (update imports)
- Create: `app/platform/web/{exception_handlers,middleware,response}.py` (copies, update imports)
- Create: `app/platform/messaging/__init__.py`
- Create: `app/platform/messaging/event_bus.py` (copy, update imports)

- [ ] **Step 1: Copy web/ to platform/**

```bash
cp -r app/infrastructure/web app/platform/web
```

Edit `app/platform/web/__init__.py`: update internal imports from `app.infrastructure.web.*` to `app.platform.web.*`.

Check each file (`exception_handlers.py`, `middleware.py`, `response.py`) for imports referencing `app.core.domain.*` or `app.infrastructure.*` and note them — these stay as-is for now (they'll be updated in the bulk import update in Task 7).

- [ ] **Step 2: Create platform/messaging/ and copy event_bus.py**

```bash
mkdir -p app/platform/messaging
cp app/infrastructure/messaging/event_bus.py app/platform/messaging/event_bus.py
```

Create `app/platform/messaging/__init__.py`:
```python
"""Platform messaging — event bus implementation."""

from app.platform.messaging.event_bus import InMemoryEventBus

__all__ = ["InMemoryEventBus"]
```

Check `event_bus.py` for imports — if it imports `IEventBus` from `app.core.application.interfaces.event_bus`, update to `from app.shared.application.interfaces.event_bus import IEventBus`. Same for `BaseDomainEvent`.

- [ ] **Step 3: Verify imports**

```bash
docker-compose exec -T python python -c "from app.platform.web import APIResponse; from app.platform.messaging import InMemoryEventBus; print('OK')"
```

---

## Task 5: Move DB managers to `app/platform/persistence/`

**Files:**
- Create: `app/platform/persistence/__init__.py`
- Create: `app/platform/persistence/postgresql/__init__.py`
- Create: `app/platform/persistence/postgresql/database.py` (copy, update imports)
- Create: `app/platform/persistence/mongodb/__init__.py`
- Create: `app/platform/persistence/mongodb/database.py` (copy, update imports)

- [ ] **Step 1: Create directories + copy database managers**

```bash
mkdir -p app/platform/persistence/postgresql app/platform/persistence/mongodb
cp app/infrastructure/persistence/postgresql/database.py app/platform/persistence/postgresql/database.py
cp app/infrastructure/persistence/mongodb/database.py app/platform/persistence/mongodb/database.py
```

Create `app/platform/persistence/__init__.py`:
```python
"""Platform persistence — database connection managers."""
```

Create `app/platform/persistence/postgresql/__init__.py`:
```python
"""PostgreSQL connection manager (platform-level)."""

from app.platform.persistence.postgresql.database import (
    get_postgres_session,
    postgres_db_manager,
)

__all__ = ["postgres_db_manager", "get_postgres_session"]
```

Create `app/platform/persistence/mongodb/__init__.py`:
```python
"""MongoDB connection manager (platform-level)."""

from app.platform.persistence.mongodb.database import mongo_db_manager

__all__ = ["mongo_db_manager"]
```

- [ ] **Step 2: Check database.py files for internal imports and update**

Read both `database.py` files. If they import from `app.infrastructure.configs.*`, update to `app.platform.configs.*`.

- [ ] **Step 3: Verify imports**

```bash
docker-compose exec -T python python -c "from app.platform.persistence.postgresql import postgres_db_manager; from app.platform.persistence.mongodb import mongo_db_manager; print('OK')"
```

---

## Task 6: Move CLI to `app/platform/cli/`

**Files:**
- Create: `app/platform/cli/` (whole tree from `app/infrastructure/cli/`)

- [ ] **Step 1: Copy CLI tree**

```bash
cp -r app/infrastructure/cli app/platform/cli
```

- [ ] **Step 2: Find and update internal imports in CLI files**

```bash
rg "from app\.infrastructure" app/platform/cli/ --files-with-matches
rg "from app\.core" app/platform/cli/ --files-with-matches
```

For each match, update the import path:
- `app.infrastructure.configs` → `app.platform.configs`
- `app.infrastructure.cli` → `app.platform.cli`

Leave `app.core.*` imports as-is — they'll be updated when core code moves in later phases.

- [ ] **Step 3: Verify imports**

```bash
docker-compose exec -T python python -c "import app.platform.cli; print('OK')"
```

---

## Task 7: Bulk update ALL imports across the codebase

This is the critical task. After moving files to new locations, every file that imports from the old paths must be updated. This is a hard cut — no shims.

**Reference: old → new import path mappings:**

| Old import path | New import path |
|---|---|
| `app.core.domain.entities.base` | `app.shared.domain.base_entity` |
| `app.core.domain.events.base` | `app.shared.domain.base_event` |
| `app.core.domain.exceptions.base` | `app.shared.domain.base_exception` |
| `app.core.domain.exceptions.error_codes` | `app.shared.domain.error_codes` |
| `app.core.domain.exceptions.validation` | `app.shared.domain.validation` |
| `app.core.domain.value_objects.user_id` | `app.shared.domain.ids.user_id` |
| `app.core.domain.value_objects.role_id` | `app.shared.domain.ids.role_id` |
| `app.core.domain.value_objects.permission_id` | `app.shared.domain.ids.permission_id` |
| `app.core.domain.value_objects.log_id` | `app.shared.domain.ids.log_id` |
| `app.core.application.interfaces.event_bus` | `app.shared.application.interfaces.event_bus` |
| `app.core.application.interfaces.command_bus` | `app.shared.application.interfaces.command_bus` |
| `app.core.application.interfaces.query_bus` | `app.shared.application.interfaces.query_bus` |
| `app.infrastructure.configs` | `app.platform.configs` |
| `app.infrastructure.web` | `app.platform.web` |
| `app.infrastructure.messaging.event_bus` | `app.platform.messaging.event_bus` |
| `app.infrastructure.persistence.postgresql.database` | `app.platform.persistence.postgresql.database` |
| `app.infrastructure.persistence.mongodb.database` | `app.platform.persistence.mongodb.database` |
| `app.infrastructure.cli` | `app.platform.cli` |

- [ ] **Step 1: Update barrel export __init__.py files in app/core/**

**`app/core/domain/exceptions/__init__.py`:** Remove re-exports of `DomainException`, `EntityNotFound`, `EntityAlreadyExists` (from base), `ErrorCode` (from error_codes), `ValidationError`, `BusinessRuleViolation` (from validation). Keep re-exports of user/role/permission exceptions. Update `__all__` accordingly.

**`app/core/domain/entities/__init__.py`:** Remove `BaseEntity` re-export. Keep User/Log/Role/Permission.

**`app/core/domain/events/__init__.py`:** Remove `BaseDomainEvent` re-export. Keep specific events.

**`app/core/domain/value_objects/__init__.py`:** Remove `UserId`, `RoleId`, `PermissionId`, `LogId` re-exports. Keep Email, Username, Action, RoleName, PermissionName.

**`app/core/application/interfaces/__init__.py`:** Remove `IEventBus`, `ICommand*`, `IQuery*` re-exports. Keep `IUnitOfWork` re-export (stays for now).

- [ ] **Step 2: Bulk-update direct imports using sed**

Run each of these from the project root. They update imports in ALL `.py` files under `app/` and `tests/`:

```bash
# Shared domain moves
find app tests -name "*.py" -exec sed -i '' \
  -e 's/from app\.core\.domain\.exceptions\.base import/from app.shared.domain.base_exception import/g' \
  -e 's/from app\.core\.domain\.exceptions import.*DomainException/from app.shared.domain.base_exception import DomainException/g' \
  -e 's/from app\.core\.domain\.exceptions\.error_codes import/from app.shared.domain.error_codes import/g' \
  -e 's/from app\.core\.domain\.exceptions\.validation import/from app.shared.domain.validation import/g' \
  -e 's/from app\.core\.domain\.entities\.base import/from app.shared.domain.base_entity import/g' \
  -e 's/from app\.core\.domain\.events\.base import/from app.shared.domain.base_event import/g' \
  -e 's/from app\.core\.domain\.value_objects\.user_id import/from app.shared.domain.ids.user_id import/g' \
  -e 's/from app\.core\.domain\.value_objects\.role_id import/from app.shared.domain.ids.role_id import/g' \
  -e 's/from app\.core\.domain\.value_objects\.permission_id import/from app.shared.domain.ids.permission_id import/g' \
  -e 's/from app\.core\.domain\.value_objects\.log_id import/from app.shared.domain.ids.log_id import/g' \
  {} +

# Bus interfaces
find app tests -name "*.py" -exec sed -i '' \
  -e 's/from app\.core\.application\.interfaces\.event_bus import/from app.shared.application.interfaces.event_bus import/g' \
  -e 's/from app\.core\.application\.interfaces\.command_bus import/from app.shared.application.interfaces.command_bus import/g' \
  -e 's/from app\.core\.application\.interfaces\.query_bus import/from app.shared.application.interfaces.query_bus import/g' \
  {} +

# Platform moves
find app tests -name "*.py" -exec sed -i '' \
  -e 's/from app\.infrastructure\.configs import/from app.platform.configs import/g' \
  -e 's/from app\.infrastructure\.configs\./from app.platform.configs./g' \
  -e 's/from app\.infrastructure\.web import/from app.platform.web import/g' \
  -e 's/from app\.infrastructure\.web\./from app.platform.web./g' \
  -e 's/from app\.infrastructure\.messaging\.event_bus import/from app.platform.messaging.event_bus import/g' \
  -e 's/from app\.infrastructure\.persistence\.postgresql\.database import/from app.platform.persistence.postgresql.database import/g' \
  -e 's/from app\.infrastructure\.persistence\.mongodb\.database import/from app.platform.persistence.mongodb.database import/g' \
  -e 's/from app\.infrastructure\.cli import/from app.platform.cli import/g' \
  -e 's/from app\.infrastructure\.cli\./from app.platform.cli./g' \
  {} +
```

**IMPORTANT:** macOS `sed -i ''` syntax. If on Linux, use `sed -i` (no empty string).

- [ ] **Step 3: Handle barrel import patterns**

Some files import from barrel `__init__.py` files rather than specific modules. Search for these:

```bash
rg "from app\.core\.domain\.exceptions import" app/ tests/ --files-with-matches
rg "from app\.core\.domain\.value_objects import" app/ tests/ --files-with-matches
rg "from app\.core\.domain\.entities import" app/ tests/ --files-with-matches
rg "from app\.core\.domain\.events import" app/ tests/ --files-with-matches
rg "from app\.core\.application\.interfaces import" app/ tests/ --files-with-matches
```

For each file found, read the import line and update it:
- If it imports `DomainException`, `ErrorCode`, `ValidationError`, etc. → change source to `app.shared.domain`
- If it imports `UserId`, `RoleId`, etc. → change source to `app.shared.domain.ids`
- If it imports `BaseEntity` → change source to `app.shared.domain`
- If it imports `BaseDomainEvent` → change source to `app.shared.domain`
- If it imports `IEventBus`, `ICommand*`, `IQuery*` → change source to `app.shared.application.interfaces`
- If it imports only non-moved symbols (e.g., `UserNotFound`, `Email`) → leave as-is

- [ ] **Step 4: Verify no broken imports remain**

```bash
docker-compose exec -T python python -c "import app.main; print('main OK')"
```

If this fails, read the error trace, find the broken import, fix it. Repeat until clean.

- [ ] **Step 5: Delete old files that have been moved**

```bash
rm app/core/domain/exceptions/base.py
rm app/core/domain/exceptions/error_codes.py
rm app/core/domain/exceptions/validation.py
rm app/core/domain/entities/base.py
rm app/core/domain/events/base.py
rm app/core/domain/value_objects/user_id.py
rm app/core/domain/value_objects/role_id.py
rm app/core/domain/value_objects/permission_id.py
rm app/core/domain/value_objects/log_id.py
rm app/core/application/interfaces/event_bus.py
rm app/core/application/interfaces/command_bus.py
rm app/core/application/interfaces/query_bus.py
rm -rf app/infrastructure/configs
rm -rf app/infrastructure/web
rm app/infrastructure/messaging/event_bus.py
rm app/infrastructure/persistence/postgresql/database.py
rm app/infrastructure/persistence/mongodb/database.py
rm -rf app/infrastructure/cli
```

- [ ] **Step 6: Verify app still imports after deletion**

```bash
docker-compose exec -T python python -c "import app.main; print('main OK')"
```

If this fails, there are remaining references to deleted files. Find and fix them:
```bash
rg "app\.core\.domain\.exceptions\.base|app\.core\.domain\.exceptions\.error_codes|app\.core\.domain\.exceptions\.validation" app/ tests/
rg "app\.core\.domain\.value_objects\.(user_id|role_id|permission_id|log_id)" app/ tests/
rg "app\.core\.application\.interfaces\.(event_bus|command_bus|query_bus)" app/ tests/
rg "app\.infrastructure\.(configs|web|cli)" app/ tests/
rg "app\.infrastructure\.messaging\.event_bus" app/ tests/
rg "app\.infrastructure\.persistence\.(postgresql|mongodb)\.database" app/ tests/
```

Fix any remaining hits.

---

## Task 8: Run tests + fix any remaining issues

- [ ] **Step 1: Run the full test suite**

```bash
make test-all
```

- [ ] **Step 2: If tests fail, trace and fix import issues**

Common issues:
- Test files importing from old paths
- Barrel `__init__.py` in `app/core/domain/` (`__init__.py`) still doing `from app.core.domain.exceptions import *` — update to exclude moved items

- [ ] **Step 3: Run arch-check**

```bash
make arch-check
```

The existing contracts should still pass (they check layer boundaries which haven't changed structurally — `app.shared` and `app.platform` are not yet in any contract).

---

## Task 9: Update import-linter contracts

**Files:**
- Modify: `pyproject.toml` (the `[tool.importlinter]` section)

- [ ] **Step 1: Add contracts for shared/ and platform/**

Append to the existing `[tool.importlinter]` section, after the existing 3 contracts:

```toml
[[tool.importlinter.contracts]]
name = "Shared kernel is dependency-free"
type = "forbidden"
source_modules = ["app.shared"]
forbidden_modules = ["app.core", "app.platform", "app.presentation", "app.infrastructure"]

[[tool.importlinter.contracts]]
name = "Platform cannot import BC domain/application code"
type = "forbidden"
source_modules = ["app.platform"]
forbidden_modules = ["app.core.domain", "app.core.application"]
```

- [ ] **Step 2: Run arch-check to verify new contracts pass**

```bash
make arch-check
```

Expected: 5/5 contracts KEPT (3 existing + 2 new).

If the "Platform cannot import BC domain/application code" contract fails, it means some platform file imports from `app.core.*`. This is expected for web/exception_handlers.py (it imports domain exceptions). **For Phase 1**, relax the platform contract to only forbid `app.core.domain` imports that are NOT exception-related. Or simply document the violation and tighten it in Phase 4 when exceptions are properly relocated.

Pragmatic approach: if it fails, change the platform contract to:
```toml
[[tool.importlinter.contracts]]
name = "Platform cannot import BC domain code"
type = "forbidden"
source_modules = ["app.platform"]
forbidden_modules = ["app.core.domain", "app.core.application"]
ignore_imports = [
    "app.platform.web.exception_handlers -> app.core.domain.exceptions.user",
    "app.platform.web.exception_handlers -> app.core.domain.exceptions.role",
    "app.platform.web.exception_handlers -> app.core.domain.exceptions.permission",
]
```

These ignores will be removed in Phase 4 when exceptions move to iam/.

---

## Task 10: Commit Phase 1

- [ ] **Step 1: Verify final state**

```bash
make arch-check    # 5/5 contracts KEPT
make test-all      # 145+ passed (same as baseline)
make format-check  # passes
make lint          # passes
```

- [ ] **Step 2: Commit everything**

```bash
git add -A
git commit -m "refactor: extract shared kernel and platform from core/infrastructure

- Create app/shared/ with base classes, ID value objects, bus interfaces
- Create app/platform/ with configs, web, DB managers, event bus, CLI
- Update all imports across codebase (hard cut, no shims)
- Add import-linter contracts for shared/ and platform/ isolation

Phase 1 of BC modular monolith refactor."
```

---

## Task 11: Phase 1 verification (DoD)

- [ ] **Step 1: Verify shared/ structure exists and is importable**

```bash
docker-compose exec -T python python -c "
from app.shared.domain import BaseEntity, DomainException, ErrorCode, ValidationError
from app.shared.domain.ids import UserId, RoleId, PermissionId, LogId
from app.shared.application.interfaces import IEventBus, ICommandBus, IQueryBus
print('shared OK')
"
```

- [ ] **Step 2: Verify platform/ structure exists and is importable**

```bash
docker-compose exec -T python python -c "
from app.platform.configs import get_app_config
from app.platform.web import APIResponse
from app.platform.messaging import InMemoryEventBus
from app.platform.persistence.postgresql import postgres_db_manager
from app.platform.persistence.mongodb import mongo_db_manager
print('platform OK')
"
```

- [ ] **Step 3: Verify old files are deleted**

```bash
test ! -f app/core/domain/exceptions/base.py && echo "base.py deleted" || echo "STILL EXISTS"
test ! -f app/core/domain/value_objects/user_id.py && echo "user_id.py deleted" || echo "STILL EXISTS"
test ! -d app/infrastructure/configs && echo "configs/ deleted" || echo "STILL EXISTS"
test ! -d app/infrastructure/web && echo "web/ deleted" || echo "STILL EXISTS"
test ! -d app/infrastructure/cli && echo "cli/ deleted" || echo "STILL EXISTS"
```

All should print "deleted".

- [ ] **Step 4: Verify tests pass at baseline level**

```bash
make test-all 2>&1 | tail -3
```

Expected: `145 passed` (same as baseline in `docs/superpowers/specs/refactor-baseline.md`).

- [ ] **Step 5: Verify arch-check passes**

```bash
make arch-check
```

Expected: 5/5 contracts KEPT.

- [ ] **Step 6: Verify app still starts**

```bash
make up
# wait ~10s
curl -sf http://localhost:8080/health-check || curl -sf http://python:8000/health-check
make down
```

Expected: JSON health response.
