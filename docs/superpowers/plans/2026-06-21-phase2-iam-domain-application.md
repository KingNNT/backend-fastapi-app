# Phase 2: IAM Domain + Application — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `app/iam/` Bounded Context with domain and application layers. Move all User, Role, Permission, and Assignment code out of `app/core/` into `app/iam/`. Create `IIamUnitOfWork`. Refactor assignment handlers to use the UoW pattern. After this phase, `app/core/` contains only Log-related code.

**Architecture:** Per-aggregate subfolder pattern within `iam/domain/`. Application layer with commands, queries, handlers, read models. New `IIamUnitOfWork` extends base `IUnitOfWork` with IAM repository attributes + `assignments`. Assignment handlers change from constructor-injected repo to `handle(cmd, uow)` pattern.

**Tech Stack:** Python 3.12, Poetry, Docker-first Makefile, import-linter, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-21-bc-modular-monolith-refactor-design.md` §3, §4, §8 Phase 2.

**Prerequisite:** Phase 1 complete (shared/ and platform/ extracted).

---

## File Structure

### Files to CREATE

**`app/iam/domain/` (per-aggregate subfolders):**
```
iam/domain/
├── user/
│   ├── __init__.py
│   ├── aggregate.py           ← from core/domain/aggregates/user.py
│   ├── entity.py              ← from core/domain/entities/user.py
│   ├── value_objects.py       ← merge email.py + username.py
│   ├── events.py              ← from core/domain/events/user_events.py
│   ├── specifications.py      ← from core/domain/specifications/user_specs.py
│   ├── exceptions.py          ← from core/domain/exceptions/user.py
│   ├── repository.py          ← from core/domain/repositories/user.py
│   └── domain_service.py      ← from core/domain/services/user_domain_service.py
├── role/
│   ├── __init__.py
│   ├── aggregate.py           ← from core/domain/aggregates/role.py
│   ├── entity.py              ← from core/domain/entities/role.py
│   ├── value_objects.py       ← from core/domain/value_objects/role_name.py
│   ├── events.py              ← from core/domain/events/role_events.py
│   ├── exceptions.py          ← from core/domain/exceptions/role.py
│   ├── repository.py          ← from core/domain/repositories/role.py
│   └── domain_service.py      ← from core/domain/services/role_domain_service.py
├── permission/
│   ├── __init__.py
│   ├── aggregate.py           ← from core/domain/aggregates/permission.py
│   ├── entity.py              ← from core/domain/entities/permission.py
│   ├── value_objects.py       ← from core/domain/value_objects/permission_name.py
│   ├── events.py              ← from core/domain/events/permission_events.py
│   ├── exceptions.py          ← from core/domain/exceptions/permission.py
│   ├── repository.py          ← from core/domain/repositories/permission.py
│   └── domain_service.py      ← from core/domain/services/permission_domain_service.py
└── assignment/
    ├── __init__.py
    ├── events.py              ← extracted from role_events.py + permission_events.py (assignment-related)
    └── repository.py          ← extracted IAssignmentRepository from assignment_handlers.py
```

**`app/iam/domain/specifications/` (shared spec base):**
```
iam/domain/specifications/
├── __init__.py
└── base.py                   ← from core/domain/specifications/base.py
```

**`app/iam/application/`:**
```
iam/application/
├── __init__.py
├── commands/
│   ├── __init__.py
│   ├── user/{create,update,delete}_user.py
│   ├── role/{create,update,delete}_role.py
│   ├── permission/{create,update,delete}_permission.py
│   └── assignment/{role_assignment,permission_assignment}.py
├── queries/
│   ├── __init__.py
│   ├── user/{get,list}_user.py
│   ├── role/{get,list}_role.py
│   ├── permission/{get,list}_permission.py
│   └── assignment/get_assignments.py
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py
│   ├── role_handlers.py
│   ├── permission_handlers.py
│   └── assignment_handlers.py
├── read_models/
│   ├── __init__.py
│   ├── user_read_model.py
│   ├── role_read_model.py
│   └── permission_read_model.py
└── interfaces/
    ├── __init__.py
    ├── password_hasher.py     ← IPasswordHasher (extracted from user_handlers.py)
    └── unit_of_work.py        ← IIamUnitOfWork (new, replaces old IUnitOfWork)
```

### Files to DELETE (after moves + import updates)

All IAM-related files in `app/core/domain/` and `app/core/application/`:
- `aggregates/{user,role,permission}.py`
- `entities/{user,role,permission}.py`
- `events/{user,role,permission}_events.py`
- `exceptions/{user,role,permission}.py`
- `repositories/{user,role,permission}.py`
- `services/{user,role,permission}_domain_service.py`
- `specifications/{base,user_specs}.py`
- `value_objects/{email,username,role_name,permission_name}.py`
- `commands/{user,role,permission,assignment}/...`
- `commands/handlers/{user,role,permission,assignment}_handlers.py`
- `queries/{user,role,permission,assignment}/...`
- `queries/handlers/{user,role,permission,assignment}_handlers.py`
- `read_models/{user,role,permission}_read_model.py`
- `interfaces/unit_of_work.py`

### Files to MODIFY (infrastructure + presentation, stay in place)

- `app/infrastructure/persistence/postgresql/unit_of_work.py` — add `assignments`, update import
- `app/infrastructure/persistence/postgresql/repositories/*.py` — update domain imports
- `app/infrastructure/persistence/postgresql/mappers/*.py` — update domain imports
- `app/infrastructure/event_handlers/user_event_handlers.py` — update imports
- `app/presentation/dependencies/handlers.py` — update assignment handler DI
- `app/presentation/dependencies/repositories.py` — update IUnitOfWork import
- `app/presentation/api/v1/*.py` — update imports
- `app/presentation/dtos/*.py` — update imports
- `app/infrastructure/setup.py` — update imports
- All test files

---

## Task 1: Create `app/iam/` directory structure

- [ ] **Step 1: Create all directories**

```bash
mkdir -p app/iam/domain/{user,role,permission,assignment,specifications}
mkdir -p app/iam/application/{commands/{user,role,permission,assignment},queries/{user,role,permission,assignment},handlers,read_models,interfaces}
```

- [ ] **Step 2: Create `app/iam/__init__.py`**

```python
"""IAM Bounded Context — Identity & Access Management.

Contains aggregates for User, Role, Permission, and Assignment concepts.
This BC manages authentication and RBAC authorization.
"""
```

- [ ] **Step 3: Create `app/iam/domain/__init__.py`**

```python
"""IAM domain layer — aggregates, entities, value objects, events."""
```

- [ ] **Step 4: Create `app/iam/application/__init__.py`**

```python
"""IAM application layer — CQRS commands, queries, handlers."""
```

- [ ] **Step 5: Create all subdirectory `__init__.py` files**

Create empty `__init__.py` in every subdirectory created in Step 1:
```bash
for dir in app/iam/domain/user app/iam/domain/role app/iam/domain/permission app/iam/domain/assignment app/iam/domain/specifications app/iam/application/commands app/iam/application/commands/user app/iam/application/commands/role app/iam/application/commands/permission app/iam/application/commands/assignment app/iam/application/queries app/iam/application/queries/user app/iam/application/queries/role app/iam/application/queries/permission app/iam/application/queries/assignment app/iam/application/handlers app/iam/application/read_models app/iam/application/interfaces; do
  touch "$dir/__init__.py"
done
```

---

## Task 2: Move User domain files

Move each file from `app/core/domain/` to `app/iam/domain/user/`, updating internal imports.

- [ ] **Step 1: Move aggregate**

```bash
cp app/core/domain/aggregates/user.py app/iam/domain/user/aggregate.py
```

Update imports inside `app/iam/domain/user/aggregate.py`:
- `from app.core.domain.entities.user import User` → `from app.iam.domain.user.entity import User`
- `from app.core.domain.value_objects.email import Email` → `from app.iam.domain.user.value_objects import Email`
- `from app.iam.domain.user.value_objects import Username` (same pattern)
- `from app.shared.domain.ids.user_id import UserId` (already updated in Phase 1)
- `from app.core.domain.events.user_events import ...` → `from app.iam.domain.user.events import ...`
- `from app.core.domain.exceptions.user import InvalidUserState` → `from app.iam.domain.user.exceptions import InvalidUserState`
- `from app.shared.domain.base_event import BaseDomainEvent` (already updated)

- [ ] **Step 2: Move entity**

```bash
cp app/core/domain/entities/user.py app/iam/domain/user/entity.py
```

Update imports:
- `from app.shared.domain.ids.user_id import UserId` (already correct)
- `from app.core.domain.value_objects.email import Email` → `from app.iam.domain.user.value_objects import Email`
- `from app.core.domain.value_objects.username import Username` → `from app.iam.domain.user.value_objects import Username`
- `from app.shared.domain.base_entity import BaseEntity` (already correct)

- [ ] **Step 3: Create value_objects.py (merge email + username)**

```bash
# Concatenate email.py and username.py into one file
cat app/core/domain/value_objects/email.py > app/iam/domain/user/value_objects.py
echo "" >> app/iam/domain/user/value_objects.py
cat app/core/domain/value_objects/username.py >> app/iam/domain/user/value_objects.py
```

No import changes needed (these only import stdlib).

- [ ] **Step 4: Move events**

```bash
cp app/core/domain/events/user_events.py app/iam/domain/user/events.py
```

Update `BaseDomainEvent` import if present (should already be `app.shared.domain.base_event`).

- [ ] **Step 5: Move specifications**

```bash
cp app/core/domain/specifications/user_specs.py app/iam/domain/user/specifications.py
cp app/core/domain/specifications/base.py app/iam/domain/specifications/base.py
```

Update imports in `user_specs.py`:
- `from app.core.domain.entities.user import User` → `from app.iam.domain.user.entity import User`
- `from app.core.domain.specifications.base import Specification` → `from app.iam.domain.specifications.base import Specification`

- [ ] **Step 6: Move exceptions**

```bash
cp app/core/domain/exceptions/user.py app/iam/domain/user/exceptions.py
```

Update imports:
- `from app.shared.domain.base_exception import ...` (should already be correct from Phase 1 sed)
- `from app.shared.domain.error_codes import ErrorCode` (should already be correct)

- [ ] **Step 7: Move repository interface**

```bash
cp app/core/domain/repositories/user.py app/iam/domain/user/repository.py
```

Update imports:
- `from app.iam.domain.user.aggregate import UserAggregate` (was `app.core.domain.aggregates.user`)
- `from app.iam.domain.user.value_objects import Email` (was `app.core.domain.value_objects.email`)
- `from app.shared.domain.ids.user_id import UserId` (already correct)
- `from app.iam.domain.user.value_objects import Username` (was `app.core.domain.value_objects.username`)

- [ ] **Step 8: Move domain service**

```bash
cp app/core/domain/services/user_domain_service.py app/iam/domain/user/domain_service.py
```

Update imports to point at `app.iam.domain.user.*` and `app.shared.domain.ids.*`.

- [ ] **Step 9: Create barrel `__init__.py` for user/**

```python
"""User aggregate — domain layer for User concept."""

from app.iam.domain.user.aggregate import UserAggregate
from app.iam.domain.user.entity import User
from app.iam.domain.user.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserEmailUpdated,
    UserPasswordUpdated,
    UserUpdated,
)
from app.iam.domain.user.exceptions import (
    InvalidUserState,
    UserAlreadyExists,
    UserNotFound,
)
from app.iam.domain.user.repository import (
    IUserReadRepository,
    IUserWriteRepository,
)
from app.iam.domain.user.value_objects import Email, Username

__all__ = [
    "UserAggregate",
    "User",
    "Email",
    "Username",
    "UserCreated",
    "UserUpdated",
    "UserDeleted",
    "UserDeactivated",
    "UserActivated",
    "UserEmailUpdated",
    "UserPasswordUpdated",
    "UserNotFound",
    "UserAlreadyExists",
    "InvalidUserState",
    "IUserWriteRepository",
    "IUserReadRepository",
]
```

- [ ] **Step 10: Verify user/ package imports**

```bash
docker-compose exec -T python python -c "from app.iam.domain.user import UserAggregate, User, Email, Username; print('user domain OK')"
```

---

## Task 3: Move Role + Permission domain files

Follow the exact same pattern as Task 2 for `role/` and `permission/`. Each gets: aggregate.py, entity.py, value_objects.py, events.py, exceptions.py, repository.py, domain_service.py, and a barrel `__init__.py`.

- [ ] **Step 1: Move Role domain files**

```bash
cp app/core/domain/aggregates/role.py app/iam/domain/role/aggregate.py
cp app/core/domain/entities/role.py app/iam/domain/role/entity.py
cp app/core/domain/value_objects/role_name.py app/iam/domain/role/value_objects.py
cp app/core/domain/events/role_events.py app/iam/domain/role/events.py
cp app/core/domain/exceptions/role.py app/iam/domain/role/exceptions.py
cp app/core/domain/repositories/role.py app/iam/domain/role/repository.py
cp app/core/domain/services/role_domain_service.py app/iam/domain/role/domain_service.py
```

Update imports in each file: replace `app.core.domain.*` with `app.iam.domain.*` paths. Key mappings:
- `aggregates/role` → `app.iam.domain.role.aggregate`
- `entities/role` → `app.iam.domain.role.entity`
- `value_objects/role_name` → `app.iam.domain.role.value_objects`
- `events/role_events` → `app.iam.domain.role.events`
- `exceptions/role` → `app.iam.domain.role.exceptions`
- `repositories/role` → `app.iam.domain.role.repository`
- `services/role_domain_service` → `app.iam.domain.role.domain_service`
- `shared/domain/ids/role_id` → `app.shared.domain.ids.role_id` (already correct)

- [ ] **Step 2: Move Permission domain files**

Same pattern as Role, using permission-specific paths.

- [ ] **Step 3: Create barrel `__init__.py` for role/ and permission/**

Same pattern as user/ `__init__.py`, re-exporting the key symbols from each subpackage.

- [ ] **Step 4: Verify role/ and permission/ imports**

```bash
docker-compose exec -T python python -c "
from app.iam.domain.role import RoleAggregate, Role, RoleName
from app.iam.domain.permission import PermissionAggregate, Permission, PermissionName
print('role + permission domain OK')
"
```

---

## Task 4: Create Assignment domain files

Assignment is a relationship concept — no aggregate root, just events + repository interface.

- [ ] **Step 1: Create `app/iam/domain/assignment/repository.py`**

Move `IAssignmentRepository` Protocol from `app/core/application/commands/handlers/assignment_handlers.py` into this file:

```python
"""Assignment repository interface — defines contract for relationship operations."""

from typing import Protocol
from uuid import UUID


class IAssignmentRepository(Protocol):
    """Repository interface for assignment operations (roles and permissions)."""

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> None: ...
    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> bool: ...
    async def user_has_role(self, user_id: UUID, role_id: UUID) -> bool: ...
    async def assign_permission_to_user(self, user_id: UUID, permission_id: UUID) -> None: ...
    async def remove_permission_from_user(self, user_id: UUID, permission_id: UUID) -> bool: ...
    async def user_has_direct_permission(self, user_id: UUID, permission_id: UUID) -> bool: ...
    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> None: ...
    async def remove_permission_from_role(self, role_id: UUID, permission_id: UUID) -> bool: ...
    async def role_has_permission(self, role_id: UUID, permission_id: UUID) -> bool: ...
    async def user_exists(self, user_id: UUID) -> bool: ...
    async def role_exists(self, role_id: UUID) -> bool: ...
    async def permission_exists(self, permission_id: UUID) -> bool: ...
```

- [ ] **Step 2: Create `app/iam/domain/assignment/events.py`**

Move assignment-related events (these currently live in role_events.py and permission_events.py):

```python
"""Assignment domain events — records of role/permission assignment changes."""

from dataclasses import dataclass

from app.shared.domain.base_event import BaseDomainEvent


@dataclass(frozen=True)
class RoleAssignedToUser(BaseDomainEvent):
    user_id: str
    role_id: str

    def _payload(self) -> dict:
        return {"user_id": self.user_id, "role_id": self.role_id}


@dataclass(frozen=True)
class RoleRemovedFromUser(BaseDomainEvent):
    user_id: str
    role_id: str

    def _payload(self) -> dict:
        return {"user_id": self.user_id, "role_id": self.role_id}


@dataclass(frozen=True)
class PermissionAssignedToUser(BaseDomainEvent):
    user_id: str
    permission_id: str

    def _payload(self) -> dict:
        return {"user_id": self.user_id, "permission_id": self.permission_id}


@dataclass(frozen=True)
class PermissionRemovedFromUser(BaseDomainEvent):
    user_id: str
    permission_id: str

    def _payload(self) -> dict:
        return {"user_id": self.user_id, "permission_id": self.permission_id}


@dataclass(frozen=True)
class PermissionAssignedToRole(BaseDomainEvent):
    role_id: str
    permission_id: str

    def _payload(self) -> dict:
        return {"role_id": self.role_id, "permission_id": self.permission_id}


@dataclass(frozen=True)
class PermissionRemovedFromRole(BaseDomainEvent):
    role_id: str
    permission_id: str

    def _payload(self) -> dict:
        return {"role_id": self.role_id, "permission_id": self.permission_id}
```

- [ ] **Step 3: Create `app/iam/domain/assignment/__init__.py`**

```python
"""Assignment domain — relationship concepts between users, roles, permissions."""

from app.iam.domain.assignment.events import (
    PermissionAssignedToRole,
    PermissionAssignedToUser,
    PermissionRemovedFromRole,
    PermissionRemovedFromUser,
    RoleAssignedToUser,
    RoleRemovedFromUser,
)
from app.iam.domain.assignment.repository import IAssignmentRepository

__all__ = [
    "IAssignmentRepository",
    "RoleAssignedToUser",
    "RoleRemovedFromUser",
    "PermissionAssignedToUser",
    "PermissionRemovedFromUser",
    "PermissionAssignedToRole",
    "PermissionRemovedFromRole",
]
```

- [ ] **Step 4: Verify assignment domain imports**

```bash
docker-compose exec -T python python -c "
from app.iam.domain.assignment import IAssignmentRepository, RoleAssignedToUser
print('assignment domain OK')
"
```

---

## Task 5: Move Application layer — commands, queries, read models

- [ ] **Step 1: Move command files**

```bash
cp app/core/application/commands/user/*.py app/iam/application/commands/user/
cp app/core/application/commands/role/*.py app/iam/application/commands/role/
cp app/core/application/commands/permission/*.py app/iam/application/commands/permission/
cp app/core/application/commands/assignment/*.py app/iam/application/commands/assignment/
```

(skip `__init__.py` — already created empty ones)

- [ ] **Step 2: Move query files**

```bash
cp app/core/application/queries/user/*.py app/iam/application/queries/user/
cp app/core/application/queries/role/*.py app/iam/application/queries/role/
cp app/core/application/queries/permission/*.py app/iam/application/queries/permission/
cp app/core/application/queries/assignment/*.py app/iam/application/queries/assignment/
```

- [ ] **Step 3: Move read model files**

```bash
cp app/core/application/read_models/user_read_model.py app/iam/application/read_models/user_read_model.py
cp app/core/application/read_models/role_read_model.py app/iam/application/read_models/role_read_model.py
cp app/core/application/read_models/permission_read_model.py app/iam/application/read_models/permission_read_model.py
```

- [ ] **Step 4: Update imports in all moved application files**

Bulk update within `app/iam/application/`:
```bash
find app/iam/application -name "*.py" -exec sed -i '' \
  -e 's/from app\.core\.domain\.aggregates\.user import/from app.iam.domain.user.aggregate import/g' \
  -e 's/from app\.core\.domain\.aggregates\.role import/from app.iam.domain.role.aggregate import/g' \
  -e 's/from app\.core\.domain\.aggregates\.permission import/from app.iam.domain.permission.aggregate import/g' \
  -e 's/from app\.core\.domain\.entities\.user import/from app.iam.domain.user.entity import/g' \
  -e 's/from app\.core\.domain\.entities\.role import/from app.iam.domain.role.entity import/g' \
  -e 's/from app\.core\.domain\.entities\.permission import/from app.iam.domain.permission.entity import/g' \
  -e 's/from app\.core\.domain\.value_objects\.email import/from app.iam.domain.user.value_objects import/g' \
  -e 's/from app\.core\.domain\.value_objects\.username import/from app.iam.domain.user.value_objects import/g' \
  -e 's/from app\.core\.domain\.value_objects\.role_name import/from app.iam.domain.role.value_objects import/g' \
  -e 's/from app\.core\.domain\.value_objects\.permission_name import/from app.iam.domain.permission.value_objects import/g' \
  -e 's/from app\.core\.domain\.events\.user_events import/from app.iam.domain.user.events import/g' \
  -e 's/from app\.core\.domain\.events\.role_events import/from app.iam.domain.role.events import/g' \
  -e 's/from app\.core\.domain\.events\.permission_events import/from app.iam.domain.permission.events import/g' \
  -e 's/from app\.core\.domain\.exceptions\.user import/from app.iam.domain.user.exceptions import/g' \
  -e 's/from app\.core\.domain\.exceptions\.role import/from app.iam.domain.role.exceptions import/g' \
  -e 's/from app\.core\.domain\.exceptions\.permission import/from app.iam.domain.permission.exceptions import/g' \
  -e 's/from app\.core\.domain\.repositories\.user import/from app.iam.domain.user.repository import/g' \
  -e 's/from app\.core\.domain\.repositories\.role import/from app.iam.domain.role.repository import/g' \
  -e 's/from app\.core\.domain\.repositories\.permission import/from app.iam.domain.permission.repository import/g' \
  -e 's/from app\.core\.domain\.services\.user_domain_service import/from app.iam.domain.user.domain_service import/g' \
  -e 's/from app\.core\.domain\.services\.role_domain_service import/from app.iam.domain.role.domain_service import/g' \
  -e 's/from app\.core\.domain\.services\.permission_domain_service import/from app.iam.domain.permission.domain_service import/g' \
  -e 's/from app\.core\.domain\.services import/from app.iam.domain.user.domain_service import/g' \
  {} +
```

**IMPORTANT:** After running sed, manually verify that the `from app.core.domain.services import` pattern correctly resolves. The original code may import multiple services from the `services/__init__.py` barrel — inspect and fix as needed.

- [ ] **Step 5: Verify application commands import**

```bash
docker-compose exec -T python python -c "
from app.iam.application.commands.user.create_user import CreateUserCommand
from app.iam.application.commands.role.create_role import CreateRoleCommand
from app.iam.application.queries.user.get_user import GetUserByIdQuery
from app.iam.application.read_models.user_read_model import UserReadModel
print('application layer OK')
"
```

---

## Task 6: Move handler files + create interfaces

- [ ] **Step 1: Move handler files**

```bash
cp app/core/application/commands/handlers/user_handlers.py app/iam/application/handlers/user_handlers.py
cp app/core/application/commands/handlers/role_handlers.py app/iam/application/handlers/role_handlers.py
cp app/core/application/commands/handlers/permission_handlers.py app/iam/application/handlers/permission_handlers.py
cp app/core/application/commands/handlers/assignment_handlers.py app/iam/application/handlers/assignment_handlers.py
cp app/core/application/queries/handlers/user_handlers.py app/iam/application/handlers/user_query_handlers.py
cp app/core/application/queries/handlers/role_handlers.py app/iam/application/handlers/role_query_handlers.py
cp app/core/application/queries/handlers/permission_handlers.py app/iam/application/handlers/permission_query_handlers.py
cp app/core/application/queries/handlers/assignment_handlers.py app/iam/application/handlers/assignment_query_handlers.py
```

Note: query handlers are renamed to `*_query_handlers.py` to avoid name clash with command handlers in the same directory.

- [ ] **Step 2: Update imports in handler files**

Run the same sed command from Task 5 Step 4 on `app/iam/application/handlers/`.

- [ ] **Step 3: Extract IPasswordHasher**

Create `app/iam/application/interfaces/password_hasher.py`:
```python
"""Password hasher interface — IAM-specific infrastructure contract."""

from typing import Protocol


class IPasswordHasher(Protocol):
    """Interface for password hashing."""

    def hash(self, password: str) -> str:
        """Hash a password."""
        ...

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        ...
```

- [ ] **Step 4: Update user_handlers.py to import IPasswordHasher from new location**

In `app/iam/application/handlers/user_handlers.py`, replace the inline `IPasswordHasher` Protocol with:
```python
from app.iam.application.interfaces.password_hasher import IPasswordHasher
```

- [ ] **Step 5: Create barrel `__init__.py` for handlers/**

```python
"""IAM application handlers — command and query handlers."""

from app.iam.application.handlers.assignment_handlers import (
    AssignPermissionToRoleHandler,
    AssignPermissionToUserHandler,
    AssignRoleToUserHandler,
    RemovePermissionFromRoleHandler,
    RemovePermissionFromUserHandler,
    RemoveRoleFromUserHandler,
)
from app.iam.application.handlers.assignment_query_handlers import (
    GetRolePermissionsHandler,
    GetUserEffectivePermissionsHandler,
    GetUserRolesHandler,
)
from app.iam.application.handlers.permission_handlers import (
    CreatePermissionHandler,
    DeletePermissionHandler,
    UpdatePermissionHandler,
)
from app.iam.application.handlers.permission_query_handlers import (
    GetPermissionByIdHandler,
    GetPermissionByNameHandler,
    ListPermissionsHandler,
)
from app.iam.application.handlers.role_handlers import (
    CreateRoleHandler,
    DeleteRoleHandler,
    UpdateRoleHandler,
)
from app.iam.application.handlers.role_query_handlers import (
    GetRoleByIdHandler,
    GetRoleByNameHandler,
    ListRolesHandler,
)
from app.iam.application.handlers.user_handlers import (
    CreateUserHandler,
    DeleteUserHandler,
    UpdateUserHandler,
)
from app.iam.application.handlers.user_query_handlers import (
    GetUserByEmailHandler,
    GetUserByIdHandler,
    GetUserByUsernameHandler,
    ListUsersHandler,
)

__all__ = [
    # User command handlers
    "CreateUserHandler",
    "UpdateUserHandler",
    "DeleteUserHandler",
    # User query handlers
    "GetUserByIdHandler",
    "GetUserByEmailHandler",
    "GetUserByUsernameHandler",
    "ListUsersHandler",
    # Role command handlers
    "CreateRoleHandler",
    "UpdateRoleHandler",
    "DeleteRoleHandler",
    # Role query handlers
    "GetRoleByIdHandler",
    "GetRoleByNameHandler",
    "ListRolesHandler",
    # Permission command handlers
    "CreatePermissionHandler",
    "UpdatePermissionHandler",
    "DeletePermissionHandler",
    # Permission query handlers
    "GetPermissionByIdHandler",
    "GetPermissionByNameHandler",
    "ListPermissionsHandler",
    # Assignment command handlers
    "AssignRoleToUserHandler",
    "RemoveRoleFromUserHandler",
    "AssignPermissionToUserHandler",
    "RemovePermissionFromUserHandler",
    "AssignPermissionToRoleHandler",
    "RemovePermissionFromRoleHandler",
    # Assignment query handlers
    "GetUserRolesHandler",
    "GetUserEffectivePermissionsHandler",
    "GetRolePermissionsHandler",
]
```

---

## Task 7: Create `IIamUnitOfWork` + update PostgresUnitOfWork

- [ ] **Step 1: Create `app/iam/application/interfaces/unit_of_work.py`**

```python
"""IAM Unit of Work interface — coordinates IAM transactions."""

from typing import Protocol, Self, runtime_checkable

from app.iam.domain.assignment.repository import IAssignmentRepository
from app.iam.domain.permission.repository import (
    IPermissionReadRepository,
    IPermissionWriteRepository,
)
from app.iam.domain.role.repository import IRoleReadRepository, IRoleWriteRepository
from app.iam.domain.user.repository import IUserReadRepository, IUserWriteRepository
from app.shared.application.interfaces.unit_of_work import IUnitOfWork


@runtime_checkable
class IIamUnitOfWork(IUnitOfWork, Protocol):
    """IAM Unit of Work — exposes IAM repositories within a transaction.

    Extends base IUnitOfWork with IAM-specific repository attributes.
    """

    # Write repositories
    users: IUserWriteRepository
    roles: IRoleWriteRepository
    permissions: IPermissionWriteRepository
    assignments: IAssignmentRepository

    # Read repositories (for validation during commands)
    users_read: IUserReadRepository
    roles_read: IRoleReadRepository
    permissions_read: IPermissionReadRepository
```

Note: This Protocol inherits from `IUnitOfWork` (base, from shared/) but re-declares the methods as part of the combined interface. Since Python Protocols use structural typing, the `IIamUnitOfWork` is satisfied by any class that has all the attributes/methods of both `IUnitOfWork` and the IAM-specific repos.

- [ ] **Step 2: Create `app/iam/application/interfaces/__init__.py`**

```python
"""IAM application interfaces."""

from app.iam.application.interfaces.password_hasher import IPasswordHasher
from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork

__all__ = ["IIamUnitOfWork", "IPasswordHasher"]
```

- [ ] **Step 3: Update PostgresUnitOfWork to add assignments + implement IIamUnitOfWork**

In `app/infrastructure/persistence/postgresql/unit_of_work.py`:

1. Update import: `from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork` (reference only, don't need to inherit explicitly since it's a Protocol)

2. Add `assignments` attribute and initialization:

In the class docstring/attributes section, add:
```python
assignments: IAssignmentRepository
```

In `_init_repositories`, add:
```python
from app.iam.domain.assignment.repository import IAssignmentRepository  # type-only
from app.infrastructure.persistence.postgresql.repositories.assignment import AssignmentRepository
self.assignments = AssignmentRepository(session)
```

- [ ] **Step 4: Verify UoW works**

```bash
docker-compose exec -T python python -c "
from app.iam.application.interfaces import IIamUnitOfWork, IPasswordHasher
print('IIamUnitOfWork OK')
"
```

---

## Task 8: Refactor Assignment handlers to use UoW pattern

This is a behavioral change — assignment handlers now receive `uow` via `handle()` instead of constructor-injected repo.

- [ ] **Step 1: Refactor `app/iam/application/handlers/assignment_handlers.py`**

For each handler class, make these changes:

**AssignRoleToUserHandler:**
```python
class AssignRoleToUserHandler:
    """Handler for AssignRoleToUserCommand."""

    async def handle(self, command: AssignRoleToUserCommand, uow: IIamUnitOfWork) -> bool:
        user_id = UUID(command.user_id)
        role_id = UUID(command.role_id)

        if not await uow.assignments.user_exists(user_id):
            raise UserNotFound(command.user_id)
        if not await uow.assignments.role_exists(role_id):
            raise RoleNotFound(command.role_id)

        if await uow.assignments.user_has_role(user_id, role_id):
            return False

        await uow.assignments.assign_role_to_user(user_id, role_id)
        uow.add_event(RoleAssignedToUser(user_id=command.user_id, role_id=command.role_id))
        return True
```

Apply the same pattern to ALL 6 assignment handlers:
- Remove `__init__` (no more constructor deps)
- Change `handle(self, command)` → `handle(self, command, uow: IIamUnitOfWork)`
- Replace `self._assignment_repository` → `uow.assignments`
- Replace `self._event_bus.publish(event)` → `uow.add_event(event)`

- [ ] **Step 2: Update DI providers for assignment handlers**

In `app/presentation/dependencies/handlers.py`, change all 6 assignment handler factory functions:

```python
# OLD:
def get_assign_role_to_user_handler(
    assignment_repository=Depends(get_assignment_repository),
    event_bus=Depends(get_event_bus),
) -> AssignRoleToUserHandler:
    return AssignRoleToUserHandler(
        assignment_repository=assignment_repository,
        event_bus=event_bus,
    )

# NEW:
def get_assign_role_to_user_handler() -> AssignRoleToUserHandler:
    return AssignRoleToUserHandler()
```

Also update the import path for all handlers from `app.core.application.commands.handlers` to `app.iam.application.handlers`.

- [ ] **Step 3: Verify assignment handlers can be constructed**

```bash
docker-compose exec -T python python -c "
from app.iam.application.handlers import AssignRoleToUserHandler
h = AssignRoleToUserHandler()
print('assignment handler OK')
"
```

---

## Task 9: Bulk update ALL remaining imports

After all IAM code is in `app/iam/`, update every file outside `app/iam/` that still imports from `app.core.*` for IAM concepts.

- [ ] **Step 1: Find all files with stale IAM imports**

```bash
rg "from app\.core\.(domain|application)" app/ tests/ --files-with-matches | \
  grep -v "app/core/" | grep -v "__pycache__"
```

- [ ] **Step 2: Bulk sed update for domain imports**

```bash
find app tests -name "*.py" -not -path "app/iam/*" -not -path "app/core/*" -exec sed -i '' \
  -e 's/from app\.core\.domain\.aggregates\.user import/from app.iam.domain.user.aggregate import/g' \
  -e 's/from app\.core\.domain\.aggregates\.role import/from app.iam.domain.role.aggregate import/g' \
  -e 's/from app\.core\.domain\.aggregates\.permission import/from app.iam.domain.permission.aggregate import/g' \
  -e 's/from app\.core\.domain\.entities\.user import/from app.iam.domain.user.entity import/g' \
  -e 's/from app\.core\.domain\.entities\.role import/from app.iam.domain.role.entity import/g' \
  -e 's/from app\.core\.domain\.entities\.permission import/from app.iam.domain.permission.entity import/g' \
  -e 's/from app\.core\.domain\.value_objects\.email import/from app.iam.domain.user.value_objects import/g' \
  -e 's/from app\.core\.domain\.value_objects\.username import/from app.iam.domain.user.value_objects import/g' \
  -e 's/from app\.core\.domain\.value_objects\.role_name import/from app.iam.domain.role.value_objects import/g' \
  -e 's/from app\.core\.domain\.value_objects\.permission_name import/from app.iam.domain.permission.value_objects import/g' \
  -e 's/from app\.core\.domain\.events\.user_events import/from app.iam.domain.user.events import/g' \
  -e 's/from app\.core\.domain\.events\.role_events import/from app.iam.domain.role.events import/g' \
  -e 's/from app\.core\.domain\.events\.permission_events import/from app.iam.domain.permission.events import/g' \
  -e 's/from app\.core\.domain\.exceptions\.user import/from app.iam.domain.user.exceptions import/g' \
  -e 's/from app\.core\.domain\.exceptions\.role import/from app.iam.domain.role.exceptions import/g' \
  -e 's/from app\.core\.domain\.exceptions\.permission import/from app.iam.domain.permission.exceptions import/g' \
  -e 's/from app\.core\.domain\.repositories\.user import/from app.iam.domain.user.repository import/g' \
  -e 's/from app\.core\.domain\.repositories\.role import/from app.iam.domain.role.repository import/g' \
  -e 's/from app\.core\.domain\.repositories\.permission import/from app.iam.domain.permission.repository import/g' \
  -e 's/from app\.core\.domain\.services import/from app.iam.domain.user.domain_service import/g' \
  -e 's/from app\.core\.domain\.services\.user_domain_service import/from app.iam.domain.user.domain_service import/g' \
  -e 's/from app\.core\.domain\.services\.role_domain_service import/from app.iam.domain.role.domain_service import/g' \
  -e 's/from app\.core\.domain\.services\.permission_domain_service import/from app.iam.domain.permission.domain_service import/g' \
  {} +
```

- [ ] **Step 3: Bulk sed update for application imports**

```bash
find app tests -name "*.py" -not -path "app/iam/*" -not -path "app/core/*" -exec sed -i '' \
  -e 's/from app\.core\.application\.commands\.handlers import/from app.iam.application.handlers import/g' \
  -e 's/from app\.core\.application\.queries\.handlers import/from app.iam.application.handlers import/g' \
  -e 's/from app\.core\.application\.commands\.user import/from app.iam.application.commands.user import/g' \
  -e 's/from app\.core\.application\.commands\.role import/from app.iam.application.commands.role import/g' \
  -e 's/from app\.core\.application\.commands\.permission import/from app.iam.application.commands.permission import/g' \
  -e 's/from app\.core\.application\.commands\.assignment import/from app.iam.application.commands.assignment import/g' \
  -e 's/from app\.core\.application\.queries\.user import/from app.iam.application.queries.user import/g' \
  -e 's/from app\.core\.application\.queries\.role import/from app.iam.application.queries.role import/g' \
  -e 's/from app\.core\.application\.queries\.permission import/from app.iam.application.queries.permission import/g' \
  -e 's/from app\.core\.application\.queries\.assignment import/from app.iam.application.queries.assignment import/g' \
  -e 's/from app\.core\.application\.read_models import/from app.iam.application.read_models import/g' \
  -e 's/from app\.core\.application\.read_models\.user_read_model import/from app.iam.application.read_models.user_read_model import/g' \
  -e 's/from app\.core\.application\.read_models\.role_read_model import/from app.iam.application.read_models.role_read_model import/g' \
  -e 's/from app\.core\.application\.read_models\.permission_read_model import/from app.iam.application.read_models.permission_read_model import/g' \
  -e 's/from app\.core\.application\.interfaces import/from app.iam.application.interfaces import/g' \
  -e 's/from app\.core\.application\.interfaces\.unit_of_work import.*IUnitOfWork/from app.iam.application.interfaces.unit_of_work import IIamUnitOfWork/g' \
  {} +
```

**IMPORTANT:** The `IUnitOfWork → IIamUnitOfWork` rename only applies to IAM usage. The shared `IUnitOfWork` (base protocol in `app/shared/`) still exists. Manually verify each file that used `IUnitOfWork` to determine if it should now use `IIamUnitOfWork`.

- [ ] **Step 4: Handle barrel imports from `app.core.domain` and `app.core.application`**

Search for barrel imports and update them:
```bash
rg "from app\.core\.(domain|application) import" app/ tests/ --files-with-matches | grep -v "app/core/"
```

For each file found, read the import and split it into:
- IAM items → import from `app.iam.domain.*` or `app.iam.application.*`
- Log items → keep importing from `app.core.*` (Log stays in core until Phase 4)

- [ ] **Step 5: Update infrastructure files**

Key files to check:
- `app/infrastructure/persistence/postgresql/repositories/*.py` — update domain entity/aggregate imports
- `app/infrastructure/persistence/postgresql/mappers/*.py` — update domain imports
- `app/infrastructure/persistence/postgresql/unit_of_work.py` — update repo interface imports
- `app/infrastructure/event_handlers/user_event_handlers.py` — update event + command imports
- `app/infrastructure/setup.py` — update all imports

- [ ] **Step 6: Verify no stale IAM references remain**

```bash
# These should return 0 (only Log-related references to app.core should remain)
rg "from app\.core\.domain\.(aggregates|entities|events|exceptions|repositories|services|specifications|value_objects)\.(user|role|permission)" app/ tests/ | wc -l
rg "from app\.core\.application\.(commands|queries|handlers|read_models)\.(user|role|permission|assignment)" app/ tests/ | wc -l
```

---

## Task 10: Delete old IAM code from `app/core/`

- [ ] **Step 1: Delete IAM domain files**

```bash
rm app/core/domain/aggregates/user.py
rm app/core/domain/aggregates/role.py
rm app/core/domain/aggregates/permission.py
rm app/core/domain/entities/user.py
rm app/core/domain/entities/role.py
rm app/core/domain/entities/permission.py
rm app/core/domain/events/user_events.py
rm app/core/domain/events/role_events.py
rm app/core/domain/events/permission_events.py
rm app/core/domain/exceptions/user.py
rm app/core/domain/exceptions/role.py
rm app/core/domain/exceptions/permission.py
rm app/core/domain/repositories/user.py
rm app/core/domain/repositories/role.py
rm app/core/domain/repositories/permission.py
rm app/core/domain/services/user_domain_service.py
rm app/core/domain/services/role_domain_service.py
rm app/core/domain/services/permission_domain_service.py
rm app/core/domain/specifications/user_specs.py
rm app/core/domain/specifications/base.py
rm app/core/domain/value_objects/email.py
rm app/core/domain/value_objects/username.py
rm app/core/domain/value_objects/role_name.py
rm app/core/domain/value_objects/permission_name.py
```

- [ ] **Step 2: Delete IAM application files**

```bash
rm -rf app/core/application/commands/user
rm -rf app/core/application/commands/role
rm -rf app/core/application/commands/permission
rm -rf app/core/application/commands/assignment
rm app/core/application/commands/handlers/user_handlers.py
rm app/core/application/commands/handlers/role_handlers.py
rm app/core/application/commands/handlers/permission_handlers.py
rm app/core/application/commands/handlers/assignment_handlers.py
rm -rf app/core/application/queries/user
rm -rf app/core/application/queries/role
rm -rf app/core/application/queries/permission
rm -rf app/core/application/queries/assignment
rm app/core/application/queries/handlers/user_handlers.py
rm app/core/application/queries/handlers/role_handlers.py
rm app/core/application/queries/handlers/permission_handlers.py
rm app/core/application/queries/handlers/assignment_handlers.py
rm app/core/application/read_models/user_read_model.py
rm app/core/application/read_models/role_read_model.py
rm app/core/application/read_models/permission_read_model.py
rm app/core/application/interfaces/unit_of_work.py
```

- [ ] **Step 3: Update barrel `__init__.py` files in `app/core/`**

Update `app/core/domain/__init__.py` to only export Log-related items.
Update `app/core/application/__init__.py` to only export Log-related items.
Update any remaining sub-barrel `__init__.py` files (exceptions, events, etc.) to remove IAM re-exports.

- [ ] **Step 4: Verify `app/core/` only contains Log code**

```bash
find app/core -name "*.py" -not -name "__init__.py" -not -path "*__pycache__*" | sort
```

Expected: only `aggregates/log.py`, `entities/log.py`, `events/log_events.py`, `repositories/log.py`, `value_objects/action.py`, `commands/log/create_log.py`, `commands/handlers/log_handlers.py`, `queries/log/*`, `queries/handlers/log_handlers.py`, `read_models/log_read_model.py`.

---

## Task 11: Update tests

- [ ] **Step 1: Run tests and identify failures**

```bash
make test-all 2>&1 | tail -30
```

- [ ] **Step 2: Fix import failures in test files**

Common issues:
- Test files importing from `app.core.domain.aggregates.user` → `app.iam.domain.user.aggregate`
- Test files importing from `app.core.domain.value_objects` barrel → split between `app.iam.domain.user.value_objects` and `app.shared.domain.ids`
- Test files importing from `app.core.application.commands.handlers` → `app.iam.application.handlers`
- Assignment handler tests that construct handlers with constructor args → remove args
- Assignment handler tests that call `handle(command)` → add `uow` param

- [ ] **Step 3: Re-run until green**

```bash
make test-all
```

Expected: 145 passed (same as baseline).

---

## Task 12: Update import-linter contracts

- [ ] **Step 1: Update `pyproject.toml` contracts**

Add IAM layer boundary contracts:

```toml
[[tool.importlinter.contracts]]
name = "IAM layer boundaries"
type = "layers"
layers = [
    "app.iam.presentation",
    "app.iam.application",
    "app.iam.domain",
]

[[tool.importlinter.contracts]]
name = "IAM domain has no infrastructure imports"
type = "forbidden"
source_modules = ["app.iam.domain"]
forbidden_modules = [
    "app.iam.infrastructure",
    "app.infrastructure",
    "app.presentation",
    "fastapi",
    "sqlmodel",
    "sqlalchemy",
    "beanie",
    "motor",
]
```

- [ ] **Step 2: Run arch-check**

```bash
make arch-check
```

Expected: 7/7 contracts KEPT (5 existing + 2 new).

Note: `app.iam.presentation` doesn't exist yet (Phase 3). The layers contract may warn about missing layers — if so, either create empty placeholder directories or add `app.iam.presentation` to the layers list in Phase 3. For now, if the contract fails because the layer doesn't exist, comment it out and add a TODO for Phase 3.

---

## Task 13: Commit Phase 2

- [ ] **Step 1: Final verification**

```bash
make arch-check    # all contracts KEPT
make test-all      # 145 passed
make format-check  # passes
make lint          # passes
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "refactor: create IAM Bounded Context with domain + application layers

- Create app/iam/domain/ with per-aggregate subfolders (user, role, permission, assignment)
- Create app/iam/application/ with commands, queries, handlers, read models
- Create IIamUnitOfWork extending IUnitOfWork with IAM repositories + assignments
- Refactor assignment handlers to use UoW pattern (handle(cmd, uow))
- Extract IPasswordHasher to iam/application/interfaces/
- Move all IAM code out of app/core/ (hard cut)
- Update all imports across codebase
- Update PostgresUnitOfWork to include assignments repository
- All 145 tests pass, 7/7 architectural contracts kept

Phase 2 of BC modular monolith refactor."
```

---

## Task 14: Phase 2 verification (DoD)

- [ ] **Step 1: Verify `app/iam/` exists with all 4 layers (domain + application)**

```bash
test -d app/iam/domain/user && echo "user domain OK" || echo "MISSING"
test -d app/iam/domain/role && echo "role domain OK" || echo "MISSING"
test -d app/iam/domain/permission && echo "permission domain OK" || echo "MISSING"
test -d app/iam/domain/assignment && echo "assignment domain OK" || echo "MISSING"
test -d app/iam/application/commands && echo "commands OK" || echo "MISSING"
test -d app/iam/application/handlers && echo "handlers OK" || echo "MISSING"
test -f app/iam/application/interfaces/unit_of_work.py && echo "IIamUnitOfWork OK" || echo "MISSING"
```

- [ ] **Step 2: Verify `app/core/` only contains Log code**

```bash
find app/core -name "*.py" -not -name "__init__.py" -not -path "*__pycache__*" | sort
```

Expected: only log-related files.

- [ ] **Step 3: Verify tests pass at baseline**

```bash
make test-all 2>&1 | tail -3
```

Expected: `145 passed`.

- [ ] **Step 4: Verify arch-check**

```bash
make arch-check
```

Expected: all contracts KEPT.

- [ ] **Step 5: Verify app still starts**

```bash
docker-compose exec -T python python -c "import app.main; print('main OK')"
```

Expected: `main OK`.
