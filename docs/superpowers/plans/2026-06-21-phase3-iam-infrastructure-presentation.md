# Phase 3: IAM Infrastructure + Presentation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move all IAM-related infrastructure (PostgreSQL models/mappers/repositories) and presentation (API routers, dependencies, DTOs) from `app/infrastructure/` and `app/presentation/` into `app/iam/`. After this phase, `app/presentation/` only contains system/health endpoints, and `app/infrastructure/` only contains platform setup + Log infrastructure.

**Architecture:** Physical file moves + import updates. `PostgresIamUnitOfWork` (renamed from `PostgresUnitOfWork`) lives in `iam/infrastructure/persistence/postgresql/unit_of_work.py`. Each BC owns its own router, dependency providers, and DTOs.

**Tech Stack:** Python 3.12, Poetry, Docker-first Makefile, import-linter, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-21-bc-modular-monolith-refactor-design.md` §3, §8 Phase 3.

**Prerequisite:** Phase 2 complete (IAM domain + application layers exist).

---

## File Structure

### Files to CREATE

```
app/iam/infrastructure/
├── persistence/
│   └── postgresql/
│       ├── __init__.py
│       ├── helpers.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── permission.py
│       │   ├── role.py
│       │   ├── role_has_permissions.py
│       │   ├── user.py
│       │   ├── user_has_permission.py
│       │   └── user_has_role.py
│       ├── mappers/
│       │   ├── __init__.py
│       │   ├── permission.py
│       │   ├── role.py
│       │   └── user.py
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── assignment_repository.py
│       │   ├── permission_read.py
│       │   ├── permission_write.py
│       │   ├── role_read.py
│       │   ├── role_write.py
│       │   ├── user_read.py
│       │   └── user_write.py
│       ├── unit_of_work.py          ← renamed PostgresUnitOfWork → PostgresIamUnitOfWork
│       └── seeds/
│           ├── __init__.py
│           ├── seed_runner.py
│           └── user_seeder.py
└── messaging/
    └── password_hasher.py          ← SimplePasswordHasher

app/iam/presentation/
├── api/
│   ├── __init__.py                 ← IAM router aggregator
│   ├── user.py
│   ├── role.py
│   ├── permission.py
│   └── assignment.py               ← extracted from user.py + role.py (path-param endpoints)
├── dependencies/
│   ├── __init__.py
│   ├── handlers.py                 ← IAM handler factory functions + *HandlerDep aliases
│   ├── repositories.py             ← IIamUnitOfWorkDep, IAM repo factories
│   └── services.py                 ← PasswordHasherDep
└── dtos/
    ├── __init__.py
    ├── user.py
    ├── role.py
    ├── permission.py
    └── assignment.py
```

### Files to DELETE (after moves + import updates)

- `app/infrastructure/persistence/postgresql/models/{permission,role,role_has_permissions,user,user_has_permission,user_has_role}.py`
- `app/infrastructure/persistence/postgresql/models/base.py`
- `app/infrastructure/persistence/postgresql/mappers/{permission,role,user}.py`
- `app/infrastructure/persistence/postgresql/repositories/assignment_repository.py`
- `app/infrastructure/persistence/postgresql/repositories/{permission,role,user}_{read,write}.py`
- `app/infrastructure/persistence/postgresql/unit_of_work.py` (moved + renamed)
- `app/infrastructure/persistence/postgresql/helpers.py` (moved)
- `app/infrastructure/persistence/postgresql/seeds/seed_runner.py` (moved)
- `app/infrastructure/persistence/postgresql/seeds/user_seeder.py` (moved)
- `app/infrastructure/messaging/password_hasher.py` (moved)
- `app/presentation/api/v1/user.py`, `role.py`, `permission.py`
- `app/presentation/dependencies/handlers.py`, `repositories.py`, `services.py` (split per BC)
- `app/presentation/dtos/{user,role,permission}.py`

### Files NOT moved (staying in `app/presentation/` and `app/infrastructure/`)

- `app/presentation/api/system.py` (health/version)
- `app/presentation/dtos/{system,response}.py` (generic system DTOs)
- `app/presentation/api/v1/log.py` (Log endpoints — will move to audit/ in Phase 4)
- `app/presentation/dtos/log.py` (Log DTO — will move in Phase 4)
- `app/infrastructure/setup.py` (composition root — gets updated, not moved)
- `app/infrastructure/persistence/postgresql/__init__.py` (becomes empty or removed)
- `app/infrastructure/persistence/mongodb/` (all of it — Phase 4)
- `app/infrastructure/persistence/postgresql/migrations/` (alembic — Phase 4)
- `app/infrastructure/event_handlers/` (cross-BC glue — Phase 4)

---

## Task 1: Create `app/iam/infrastructure/` directory structure

- [ ] **Step 1: Create directories**

```bash
mkdir -p app/iam/infrastructure/persistence/postgresql/{models,mappers,repositories,seeds}
mkdir -p app/iam/infrastructure/messaging
mkdir -p app/iam/presentation/{api,dependencies,dtos}
```

- [ ] **Step 2: Create empty `__init__.py` files**

Create `__init__.py` in every new directory:
```bash
for d in app/iam/infrastructure app/iam/infrastructure/persistence app/iam/infrastructure/persistence/postgresql app/iam/infrastructure/persistence/postgresql/models app/iam/infrastructure/persistence/postgresql/mappers app/iam/infrastructure/persistence/postgresql/repositories app/iam/infrastructure/persistence/postgresql/seeds app/iam/infrastructure/messaging app/iam/presentation app/iam/presentation/api app/iam/presentation/dependencies app/iam/presentation/dtos; do
  touch "$d/__init__.py"
done
```

---

## Task 2: Move IAM PostgreSQL models

Move 6 model files (Permission, Role, RoleHasPermissions, User, UserHasPermission, UserHasRole) + base.py.

- [ ] **Step 1: Move models**

```bash
git mv app/infrastructure/persistence/postgresql/models/base.py app/iam/infrastructure/persistence/postgresql/models/base.py
git mv app/infrastructure/persistence/postgresql/models/permission.py app/iam/infrastructure/persistence/postgresql/models/permission.py
git mv app/infrastructure/persistence/postgresql/models/role.py app/iam/infrastructure/persistence/postgresql/models/role.py
git mv app/infrastructure/persistence/postgresql/models/role_has_permissions.py app/iam/infrastructure/persistence/postgresql/models/role_has_permissions.py
git mv app/infrastructure/persistence/postgresql/models/user.py app/iam/infrastructure/persistence/postgresql/models/user.py
git mv app/infrastructure/persistence/postgresql/models/user_has_permission.py app/iam/infrastructure/persistence/postgresql/models/user_has_permission.py
git mv app/infrastructure/persistence/postgresql/models/user_has_role.py app/iam/infrastructure/persistence/postgresql/models/user_has_role.py
```

- [ ] **Step 2: Update imports inside moved models**

```bash
find app/iam/infrastructure/persistence/postgresql/models -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain\.|from app.iam.domain.|g' \
  {} +
echo "Model imports updated"
```

- [ ] **Step 3: Verify models import**

```bash
docker-compose exec -T python python -c "
from app.iam.infrastructure.persistence.postgresql.models import UserModel, RoleModel, PermissionModel
print('models OK')
" 2>&1 | tail -5
```

---

## Task 3: Move IAM PostgreSQL mappers

- [ ] **Step 1: Move mappers**

```bash
git mv app/infrastructure/persistence/postgresql/mappers/permission.py app/iam/infrastructure/persistence/postgresql/mappers/permission.py
git mv app/infrastructure/persistence/postgresql/mappers/role.py app/iam/infrastructure/persistence/postgresql/mappers/role.py
git mv app/infrastructure/persistence/postgresql/mappers/user.py app/iam/infrastructure/persistence/postgresql/mappers/user.py
```

- [ ] **Step 2: Update imports inside moved mappers**

```bash
find app/iam/infrastructure/persistence/postgresql/mappers -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain\.|from app.iam.domain.|g' \
  -e 's|from app\.infrastructure\.persistence\.postgresql\.models|from app.iam.infrastructure.persistence.postgresql.models|g' \
  {} +
```

- [ ] **Step 3: Create barrel `__init__.py` for mappers**

```python
"""IAM PostgreSQL mappers — domain <-> ORM conversion."""

from app.iam.infrastructure.persistence.postgresql.mappers.permission import (
    PermissionMapper,
)
from app.iam.infrastructure.persistence.postgresql.mappers.role import RoleMapper
from app.iam.infrastructure.persistence.postgresql.mappers.user import UserMapper

__all__ = ["UserMapper", "RoleMapper", "PermissionMapper"]
```

(Check actual class names in the files — adjust if different.)

---

## Task 4: Move IAM PostgreSQL repositories

Move 7 repository files. Rename `assignment_repository.py` → `assignment.py` for consistency.

- [ ] **Step 1: Move repositories**

```bash
git mv app/infrastructure/persistence/postgresql/repositories/assignment_repository.py app/iam/infrastructure/persistence/postgresql/repositories/assignment.py
git mv app/infrastructure/persistence/postgresql/repositories/user_write.py app/iam/infrastructure/persistence/postgresql/repositories/user_write.py
git mv app/infrastructure/persistence/postgresql/repositories/user_read.py app/iam/infrastructure/persistence/postgresql/repositories/user_read.py
git mv app/infrastructure/persistence/postgresql/repositories/role_write.py app/iam/infrastructure/persistence/postgresql/repositories/role_write.py
git mv app/infrastructure/persistence/postgresql/repositories/role_read.py app/iam/infrastructure/persistence/postgresql/repositories/role_read.py
git mv app/infrastructure/persistence/postgresql/repositories/permission_write.py app/iam/infrastructure/persistence/postgresql/repositories/permission_write.py
git mv app/infrastructure/persistence/postgresql/repositories/permission_read.py app/iam/infrastructure/persistence/postgresql/repositories/permission_read.py
```

- [ ] **Step 2: Update imports inside moved repositories**

```bash
find app/iam/infrastructure/persistence/postgresql/repositories -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain\.|from app.iam.domain.|g' \
  -e 's|from app\.infrastructure\.persistence\.postgresql\.models|from app.iam.infrastructure.persistence.postgresql.models|g' \
  -e 's|from app\.infrastructure\.persistence\.postgresql\.mappers|from app.iam.infrastructure.persistence.postgresql.mappers|g' \
  {} +
```

Also need to update imports in `app/infrastructure/persistence/postgresql/unit_of_work.py` (which is still there but imports `from app.infrastructure.persistence.postgresql.repositories.assignment_repository` — should be `from app.iam.infrastructure.persistence.postgresql.repositories.assignment`). Update later in Task 6.

- [ ] **Step 3: Create barrel `__init__.py` for repositories**

```python
"""IAM PostgreSQL repository implementations."""

from app.iam.infrastructure.persistence.postgresql.repositories.assignment import (
    AssignmentRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.permission_read import (
    PostgresPermissionReadRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.permission_write import (
    PostgresPermissionWriteRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.role_read import (
    PostgresRoleReadRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.role_write import (
    PostgresRoleWriteRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.user_read import (
    PostgresUserReadRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.user_write import (
    PostgresUserWriteRepository,
)

__all__ = [
    "AssignmentRepository",
    "PostgresUserReadRepository",
    "PostgresUserWriteRepository",
    "PostgresRoleReadRepository",
    "PostgresRoleWriteRepository",
    "PostgresPermissionReadRepository",
    "PostgresPermissionWriteRepository",
]
```

(Check actual class names in the files — adjust if different.)

---

## Task 5: Move seeds and helpers

- [ ] **Step 1: Move seeds**

```bash
git mv app/infrastructure/persistence/postgresql/seeds/seed_runner.py app/iam/infrastructure/persistence/postgresql/seeds/seed_runner.py
git mv app/infrastructure/persistence/postgresql/seeds/user_seeder.py app/iam/infrastructure/persistence/postgresql/seeds/user_seeder.py
```

- [ ] **Step 2: Move helpers**

```bash
git mv app/infrastructure/persistence/postgresql/helpers.py app/iam/infrastructure/persistence/postgresql/helpers.py
```

- [ ] **Step 3: Update imports in seeds + helpers**

```bash
find app/iam/infrastructure/persistence/postgresql/seeds app/iam/infrastructure/persistence/postgresql/helpers.py -name "*.py" -exec sed -i '' \
  -e 's|from app\.infrastructure\.persistence\.postgresql\.models|from app.iam.infrastructure.persistence.postgresql.models|g' \
  -e 's|from app\.infrastructure\.persistence\.postgresql\.mappers|from app.iam.infrastructure.persistence.postgresql.mappers|g' \
  -e 's|from app\.core\.domain\.|from app.iam.domain.|g' \
  -e 's|from app\.core\.application\.|from app.iam.application.|g' \
  -e 's|from app\.infrastructure\.persistence\.seeders|from app.iam.infrastructure.persistence.postgresql.seeds|g' \
  {} +
```

---

## Task 6: Move and rename `unit_of_work.py` → `PostgresIamUnitOfWork`

- [ ] **Step 1: Move the file (and rename the class)**

```bash
git mv app/infrastructure/persistence/postgresql/unit_of_work.py app/iam/infrastructure/persistence/postgresql/unit_of_work.py
```

- [ ] **Step 2: Rename class inside the file**

In `app/iam/infrastructure/persistence/postgresql/unit_of_work.py`:
- Replace `class PostgresUnitOfWork:` → `class PostgresIamUnitOfWork:`
- Update the docstring if needed

- [ ] **Step 3: Update imports inside the file**

```bash
sed -i '' \
  -e 's|from app\.infrastructure\.persistence\.postgresql\.repositories\.assignment_repository|from app.iam.infrastructure.persistence.postgresql.repositories.assignment|g' \
  -e 's|from app\.infrastructure\.persistence\.postgresql\.repositories\.|from app.iam.infrastructure.persistence.postgresql.repositories.|g' \
  -e 's|from app\.iam\.domain\.user\.repository import|from app.iam.domain.user.repository import|g' \
  -e 's|from app\.iam\.domain\.role\.repository import|from app.iam.domain.role.repository import|g' \
  -e 's|from app\.iam\.domain\.permission\.repository import|from app.iam.domain.permission.repository import|g' \
  -e 's|from app\.iam\.domain\.assignment\.repository import|from app.iam.domain.assignment.repository import|g' \
  app/iam/infrastructure/persistence/postgresql/unit_of_work.py
```

- [ ] **Step 4: Verify UoW imports**

```bash
docker-compose exec -T python python -c "
from app.iam.infrastructure.persistence.postgresql.unit_of_work import PostgresIamUnitOfWork
print('UoW OK')
" 2>&1 | tail -5
```

---

## Task 7: Move `password_hasher.py` to IAM

- [ ] **Step 1: Move file**

```bash
git mv app/infrastructure/messaging/password_hasher.py app/iam/infrastructure/messaging/password_hasher.py
```

- [ ] **Step 2: Update imports inside (usually none, but verify)**

```bash
rg "from app\." app/iam/infrastructure/messaging/password_hasher.py
```

If there are imports, update accordingly. Most likely it has no internal imports.

- [ ] **Step 3: Verify**

```bash
docker-compose exec -T python python -c "
from app.iam.infrastructure.messaging.password_hasher import SimplePasswordHasher
print('password hasher OK')
" 2>&1 | tail -5
```

---

## Task 8: Move IAM presentation files (API routers, DTOs)

- [ ] **Step 1: Move API routers**

```bash
git mv app/presentation/api/v1/user.py app/iam/presentation/api/user.py
git mv app/presentation/api/v1/role.py app/iam/presentation/api/role.py
git mv app/presentation/api/v1/permission.py app/iam/presentation/api/permission.py
```

For the assignment endpoints (currently in user.py and role.py as sub-routes like `/v1/users/{id}/roles`), create a dedicated `assignment.py`:

```bash
touch app/iam/presentation/api/assignment.py
```

The `assignment.py` content needs to be assembled from the existing assignment-related endpoints in `user.py` and `role.py`. Read those files first, extract the assignment endpoints (`/v1/users/{user_id}/roles`, `/v1/roles/{role_id}/permissions`), and create a clean `assignment.py`.

(This is a small manual task — see the actual code in user.py/role.py for endpoint definitions to extract.)

- [ ] **Step 2: Update imports inside moved routers**

```bash
find app/iam/presentation/api -name "*.py" -exec sed -i '' \
  -e 's|from app\.iam\.application\.handlers import|from app.iam.application.handlers import|g' \
  -e 's|from app\.core\.application\.commands\.|from app.iam.application.commands.|g' \
  -e 's|from app\.core\.application\.queries\.|from app.iam.application.queries.|g' \
  -e 's|from app\.core\.domain\.|from app.iam.domain.|g' \
  {} +
```

- [ ] **Step 3: Move DTOs**

```bash
git mv app/presentation/dtos/user.py app/iam/presentation/dtos/user.py
git mv app/presentation/dtos/role.py app/iam/presentation/dtos/role.py
git mv app/presentation/dtos/permission.py app/iam/presentation/dtos/permission.py
```

Create `assignment.py` DTOs (empty for now or with simple DTOs extracted from user/role DTOs).

- [ ] **Step 4: Update imports in DTOs**

```bash
find app/iam/presentation/dtos -name "*.py" -exec sed -i '' \
  -e 's|from app\.core\.domain\.|from app.iam.domain.|g' \
  -e 's|from app\.shared\.domain\.|from app.shared.domain.|g' \
  {} +
```

---

## Task 9: Move presentation dependencies into IAM

- [ ] **Step 1: Create IAM-specific DI files**

`app/iam/presentation/dependencies/handlers.py` — copy the IAM-related portions from current `app/presentation/dependencies/handlers.py`. Includes:
- All `*HandlerDep` aliases for IAM handlers
- Factory functions for `CreateUserHandler`, `CreateRoleHandler`, etc., `GetUserByIdHandler`, etc.
- Assignment handler factories (now with no-arg constructors)
- Does NOT include Log handlers

`app/iam/presentation/dependencies/repositories.py` — copy IAM-related factories:
- `get_iam_unit_of_work`
- `get_user_read_model_repository`, `get_role_read_model_repository`, `get_permission_read_model_repository`
- (AssignmentRepository is inside the UoW now, not separate)

`app/iam/presentation/dependencies/services.py` — `get_password_hasher` factory.

- [ ] **Step 2: Update imports in new IAM DI files**

All imports pointing to `app.core.application.*` → `app.iam.application.*`. Imports from `app.iam.application.handlers.assignment_handlers` for read model interfaces need to be from `assignment_query_handlers` (where `IAssignmentQueryRepository` lives now).

- [ ] **Step 3: Create barrel `__init__.py` for dependencies**

```python
"""IAM presentation dependency providers."""

from app.iam.presentation.dependencies.handlers import (
    AssignPermissionToRoleHandlerDep,
    AssignPermissionToUserHandlerDep,
    AssignRoleToUserHandlerDep,
    CreatePermissionHandlerDep,
    CreateRoleHandlerDep,
    CreateUserHandlerDep,
    DeletePermissionHandlerDep,
    DeleteRoleHandlerDep,
    DeleteUserHandlerDep,
    GetPermissionByIdHandlerDep,
    GetPermissionByNameHandlerDep,
    GetRoleByIdHandlerDep,
    GetRoleNameHandlerDep,
    GetRolePermissionsHandlerDep,
    GetUserByEmailHandlerDep,
    GetUserByIdHandlerDep,
    GetUserByUsernameHandlerDep,
    GetUserEffectivePermissionsHandlerDep,
    GetUserRolesHandlerDep,
    ListPermissionsHandlerDep,
    ListRolesHandlerDep,
    ListUsersHandlerDep,
    RemovePermissionFromRoleHandlerDep,
    RemovePermissionFromUserHandlerDep,
    RemoveRoleFromUserHandlerDep,
    UpdatePermissionHandlerDep,
    UpdateRoleHandlerDep,
    UpdateUserHandlerDep,
)
from app.iam.presentation.dependencies.repositories import (
    IamUnitOfWorkDep,
    get_iam_unit_of_work,
)
from app.iam.presentation.dependencies.services import PasswordHasherDep

__all__ = [
    # IAM Unit of Work
    "IamUnitOfWorkDep",
    "get_iam_unit_of_work",
    # Password hasher
    "PasswordHasherDep",
    # User handlers
    "CreateUserHandlerDep",
    "UpdateUserHandlerDep",
    "DeleteUserHandlerDep",
    "GetUserByIdHandlerDep",
    "GetUserByEmailHandlerDep",
    "GetUserByUsernameHandlerDep",
    "ListUsersHandlerDep",
    # Role handlers
    "CreateRoleHandlerDep",
    "UpdateRoleHandlerDep",
    "DeleteRoleHandlerDep",
    "GetRoleByIdHandlerDep",
    "GetRoleNameHandlerDep",
    "ListRolesHandlerDep",
    # Permission handlers
    "CreatePermissionHandlerDep",
    "UpdatePermissionHandlerDep",
    "DeletePermissionHandlerDep",
    "GetPermissionByIdHandlerDep",
    "GetPermissionByNameHandlerDep",
    "ListPermissionsHandlerDep",
    # Assignment handlers
    "AssignRoleToUserHandlerDep",
    "RemoveRoleFromUserHandlerDep",
    "AssignPermissionToUserHandlerDep",
    "RemovePermissionFromUserHandlerDep",
    "AssignPermissionToRoleHandlerDep",
    "RemovePermissionFromRoleHandlerDep",
    "GetUserRolesHandlerDep",
    "GetUserEffectivePermissionsHandlerDep",
    "GetRolePermissionsHandlerDep",
]
```

---

## Task 10: Create IAM router aggregator + update `main.py`

- [ ] **Step 1: Create IAM router in `app/iam/presentation/api/__init__.py`**

```python
"""IAM API router aggregator."""

from fastapi import APIRouter

from app.iam.presentation.api import assignment, permission, role, user

router = APIRouter()
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(role.router, prefix="/roles", tags=["roles"])
router.include_router(permission.router, prefix="/permissions", tags=["permissions"])
router.include_router(assignment.router, tags=["assignments"])
```

- [ ] **Step 2: Update `app/main.py` to use BC routers**

```python
# OLD:
from app.presentation.api import api_router
app.include_router(api_router)

# NEW:
from app.iam.presentation.api import router as iam_router
from app.audit.presentation.api import router as audit_router  # Log router (still in presentation for now)
from app.presentation.api import system_router

app.include_router(iam_router, prefix="/v1")
app.include_router(audit_router, prefix="/v1")  # until Phase 4
app.include_router(system_router)
```

- [ ] **Step 3: Verify app starts**

```bash
docker-compose exec -T python python -c "import app.main; print('main OK')" 2>&1 | tail -5
```

---

## Task 11: Update infrastructure/setup.py and remaining deps

- [ ] **Step 1: Update `app/infrastructure/setup.py` imports**

Update all imports to new locations:
- `PostgresUserWriteRepository` → `app.iam.infrastructure.persistence.postgresql.repositories.user_write.PostgresUserWriteRepository`
- (etc. for all repos)
- `SimplePasswordHasher` → `app.iam.infrastructure.messaging.password_hasher.SimplePasswordHasher`
- `PostgresUnitOfWork` → `PostgresIamUnitOfWork` (and rename the variable + factory in `get_iam_unit_of_work`)

- [ ] **Step 2: Update `app/presentation/dependencies/services.py`**

If it imports IAM-related things, leave only Log handlers here. Delete IAM bits (password_hasher moves to iam BC).

- [ ] **Step 3: Delete or clean up old DI files in `app/presentation/dependencies/`**

After extracting IAM-related bits:
- Keep `app/presentation/dependencies/__init__.py` (re-export Log handler deps)
- Update `handlers.py` to only export Log handler factories
- Delete `repositories.py` if all content moved to iam (it might be empty now)
- Delete `services.py` if empty (password_hasher moved)

- [ ] **Step 4: Update `app/presentation/dtos/response.py`** (stays — generic response wrapper)

No changes needed unless it imports IAM-specific stuff.

---

## Task 12: Bulk update remaining imports across the codebase

- [ ] **Step 1: Update all imports of moved files**

```bash
find app tests -name "*.py" -not -path "app/iam/*" -not -path "app/shared/*" -not -path "app/platform/*" -exec sed -i '' \
  -e 's|app\.infrastructure\.persistence\.postgresql\.models|app.iam.infrastructure.persistence.postgresql.models|g' \
  -e 's|app\.infrastructure\.persistence\.postgresql\.mappers|app.iam.infrastructure.persistence.postgresql.mappers|g' \
  -e 's|app\.infrastructure\.persistence\.postgresql\.repositories\.assignment_repository|app.iam.infrastructure.persistence.postgresql.repositories.assignment|g' \
  -e 's|app\.infrastructure\.persistence\.postgresql\.repositories\.\(user_write\|user_read\|role_write\|role_read\|permission_write\|permission_read\)|app.iam.infrastructure.persistence.postgresql.repositories.\1|g' \
  -e 's|app\.infrastructure\.persistence\.postgresql\.helpers|app.iam.infrastructure.persistence.postgresql.helpers|g' \
  -e 's|app\.infrastructure\.persistence\.postgresql\.seeds|app.iam.infrastructure.persistence.postgresql.seeds|g' \
  -e 's|app\.infrastructure\.persistence\.postgresql\.unit_of_work import PostgresUnitOfWork|app.iam.infrastructure.persistence.postgresql.unit_of_work import PostgresIamUnitOfWork|g' \
  -e 's|app\.infrastructure\.messaging\.password_hasher|app.iam.infrastructure.messaging.password_hasher|g' \
  -e 's|app\.presentation\.api\.v1\.user|app.iam.presentation.api.user|g' \
  -e 's|app\.presentation\.api\.v1\.role|app.iam.presentation.api.role|g' \
  -e 's|app\.presentation\.api\.v1\.permission|app.iam.presentation.api.permission|g' \
  -e 's|app\.presentation\.dtos\.user|app.iam.presentation.dtos.user|g' \
  -e 's|app\.presentation\.dtos\.role|app.iam.presentation.dtos.role|g' \
  -e 's|app\.presentation\.dtos\.permission|app.iam.presentation.dtos.permission|g' \
  {} +
```

- [ ] **Step 2: Update presentation dependencies imports**

```bash
find app tests -name "*.py" -not -path "app/iam/*" -not -path "app/shared/*" -not -path "app/platform/*" -exec sed -i '' \
  -e 's|from app\.presentation\.dependencies\.handlers|from app.iam.presentation.dependencies.handlers|g' \
  -e 's|from app\.presentation\.dependencies\.repositories|from app.iam.presentation.dependencies.repositories|g' \
  -e 's|from app\.presentation\.dependencies\.services|from app.iam.presentation.dependencies.services|g' \
  {} +
```

Note: this will break Log-only deps that imported from `app.presentation.dependencies`. Log handlers must now have their own deps. Add a `app/presentation/dependencies/handlers.py` with only Log factories, or use a separate path.

- [ ] **Step 3: Verify no stale references remain**

```bash
rg "app\.infrastructure\.persistence\.postgresql\.(models|mappers|repositories|seeds|unit_of_work|helpers)" app/ tests/ \
  --files-with-matches 2>/dev/null | grep -v "app/iam/"
echo "---"
rg "app\.infrastructure\.messaging\.password_hasher" app/ tests/ | grep -v "app/iam/"
echo "---"
rg "app\.presentation\.(api\.v1\.(user|role|permission)|dtos\.(user|role|permission))" app/ tests/ | grep -v "app/iam/"
```

Expected: all empty.

---

## Task 13: Run tests + fix issues

- [ ] **Step 1: Run full test suite**

```bash
make test-all 2>&1 | tail -30
```

- [ ] **Step 2: Fix import errors**

Common issues:
- Tests importing from `app.infrastructure.persistence.postgresql.repositories.user_write` etc.
- Tests importing from old `app.presentation.dependencies.handlers`
- Tests importing from `app.iam.infrastructure.persistence.postgresql.repositories.assignment` (renamed from assignment_repository)

- [ ] **Step 3: Re-run until 145 pass**

---

## Task 14: Update import-linter contracts

- [ ] **Step 1: Uncomment and complete IAM layer boundaries**

In `pyproject.toml`, uncomment the IAM layer contract:
```toml
[[tool.importlinter.contracts]]
name = "IAM layer boundaries"
type = "layers"
layers = [
    "app.iam.presentation",
    "app.iam.application",
    "app.iam.domain",
]
```

- [ ] **Step 2: Add IAM presentation and infrastructure contracts**

```toml
[[tool.importlinter.contracts]]
name = "IAM infrastructure implements IAM interfaces"
type = "forbidden"
source_modules = ["app.iam.infrastructure"]
forbidden_modules = ["app.iam.application"]
# Infrastructure can implement interfaces and import models/mappers/repos,
# but should NOT import command/query handlers (those wire via DI at composition root).

[[tool.importlinter.contracts]]
name = "IAM presentation forbidden from infrastructure"
type = "forbidden"
source_modules = ["app.iam.presentation"]
forbidden_modules = ["app.iam.infrastructure", "app.infrastructure"]
```

- [ ] **Step 3: Run arch-check**

```bash
make arch-check 2>&1 | tail -15
```

Expected: 9/9 contracts KEPT.

---

## Task 15: Commit Phase 3

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
git commit -m "refactor: move IAM infrastructure + presentation into app/iam/

Phase 3 of BC modular monolith refactor:

Infrastructure (app/iam/infrastructure/):
- persistence/postgresql/ with models, mappers, repositories, seeds
- PostgresIamUnitOfWork (renamed from PostgresUnitOfWork)
- messaging/password_hasher.py (SimplePasswordHasher)

Presentation (app/iam/presentation/):
- api/{user,role,permission,assignment}.py
- dependencies/{handlers,repositories,services}.py with IAM-specific DI
- dtos/{user,role,permission}.py

Other changes:
- app/presentation/ shrunk to only system + log endpoints
- app/main.py includes IAM + audit + system routers
- 9/9 architectural contracts kept (added IAM layer + presentation contracts)
- All 145 tests pass (98 unit + 30 integration + 17 e2e)"
```

---

## Task 16: Phase 3 DoD verification

- [ ] **Step 1: `app/iam/infrastructure/` exists with persistence/postgresql/**

```bash
ls app/iam/infrastructure/persistence/postgresql/
```

Expected: `__init__.py`, `helpers.py`, `models/`, `mappers/`, `repositories/`, `seeds/`, `unit_of_work.py`

- [ ] **Step 2: `app/iam/presentation/` exists with api, dependencies, dtos**

```bash
ls app/iam/presentation/api/
ls app/iam/presentation/dependencies/
ls app/iam/presentation/dtos/
```

- [ ] **Step 3: `app/presentation/` only has system + log**

```bash
ls app/presentation/api/v1/
ls app/presentation/dtos/
```

Expected: only `log.py` in v1/; only `log.py`, `response.py`, `system.py` in dtos/.

- [ ] **Step 4: Tests pass**

```bash
make test-all 2>&1 | tail -3
```

- [ ] **Step 5: Arch-check 9/9**

```bash
make arch-check
```

- [ ] **Step 6: App starts**

```bash
docker-compose exec -T python python -c "import app.main; print('OK')"
```
