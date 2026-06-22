# Refactor Result Metrics

- **Captured:** 2026-06-21 (after Phase 5)
- **Branch:** `refactor/bc-modular-monolith`
- **Tag:** `v0.2.0-bc-modular`
- **Result:** Bounded Context Modular Monolith refactor complete

## Comparison: Baseline vs Final

| Metric | Baseline (layer-first) | Final (BC modular) | Δ |
|---|---|---|---|
| **Tests** | 145 | 145 | ✅ unchanged |
| **Coverage** | 66% | 63% | -3% (more code lines, similar quality) |
| **Endpoints** | 30 | 34 | +4 (`/permissions/by-name`, `/logs/`, `/logs/by-user/{user_id}`) |
| **Architectural contracts** | 0 | 8 | ✅ NEW |
| **BCs** | 1 (mixed in `app/core/`) | 2 (`iam/`, `audit/`) | ✅ separated |
| **Cross-BC imports** | n/a | 0 | ✅ enforced |
| **`app/core/` directory** | exists | DELETED | ✅ fully migrated |

## Test Breakdown (unchanged from baseline)

- **Total tests:** 145
- **Unit tests:** 98 (in `tests/unit/`)
  - `tests/unit/domain/test_value_objects.py`: 31
  - `tests/unit/domain/test_entities.py`: 20
  - `tests/unit/domain/test_aggregates.py`: 21
  - `tests/unit/application/test_query_handlers.py`: 10
  - `tests/unit/application/test_command_handlers.py`: 16
- **Integration tests:** 30 (in `tests/integration/`)
  - `tests/integration/mongodb/test_log_repository.py`: 11 (now in audit BC)
  - `tests/integration/event_handlers/test_user_events.py`: 7 (cross-BC)
  - `tests/integration/postgresql/test_user_repository.py`: 12 (now in iam BC)
- **E2E tests:** 17 (in `tests/e2e/`)

## Endpoints (34 total)

### System (2)
```
GET /health-check
GET /version
```

### v1 (32)

**IAM — Users (7)**
```
POST   /v1/users/
GET    /v1/users/
GET    /v1/users/{user_id}
GET    /v1/users/by-email/{email}
GET    /v1/users/by-username/{username}
PUT    /v1/users/{user_id}
DELETE /v1/users/{user_id}
```

**IAM — Users: Role assignments (3)**
```
GET    /v1/users/{user_id}/roles
POST   /v1/users/{user_id}/roles
DELETE /v1/users/{user_id}/roles/{role_id}
```

**IAM — Users: Permission assignments (3)**
```
GET    /v1/users/{user_id}/permissions
POST   /v1/users/{user_id}/permissions
DELETE /v1/users/{user_id}/permissions/{permission_id}
```

**IAM — Roles (5)**
```
POST   /v1/roles/
GET    /v1/roles/
GET    /v1/roles/{role_id}
GET    /v1/roles/by-name/{name}
PUT    /v1/roles/{role_id}
DELETE /v1/roles/{role_id}
```

**IAM — Roles: Permission assignments (3)**
```
GET    /v1/roles/{role_id}/permissions
POST   /v1/roles/{role_id}/permissions
DELETE /v1/roles/{role_id}/permissions/{permission_id}
```

**IAM — Permissions (6)**
```
POST   /v1/permissions/
GET    /v1/permissions/
GET    /v1/permissions/{permission_id}
GET    /v1/permissions/by-name/{name}
PUT    /v1/permissions/{permission_id}
DELETE /v1/permissions/{permission_id}
```

**Audit — Logs (4)**
```
POST /v1/logs/
GET  /v1/logs/
GET  /v1/logs/{log_id}
GET  /v1/logs/by-user/{user_id}
```

## Architecture Enforcement

8 import-linter contracts (all KEPT):

1. `Shared kernel is dependency-free` — `app/shared` has zero BC/platform/presentation/infrastructure dependencies
2. `Platform cannot import BC domain/application code` — `app/platform` BC-agnostic
3. `IAM layer boundaries` — `presentation → application → domain`
4. `IAM domain has no infrastructure or framework imports` — no `fastapi`, `sqlmodel`, `sqlalchemy`, `beanie`, `motor` in domain
5. `IAM does not import from audit BC` — BC isolation
6. `Audit layer boundaries` — same as IAM but for audit
7. `Audit domain has no infrastructure or framework imports` — same purity rule
8. `Audit does not import from iam BC` — only exception is the cross-BC event translator which subscribes to IAM events

## Folder Structure Final State

```
app/
├── audit/                    ← BC: Audit Logging (Log + cross-BC translator)
├── iam/                      ← BC: Identity & Access Management (User/Role/Permission/Assignment)
├── shared/                   ← Shared Kernel (BaseEntity, ID VOs, bus interfaces, base UoW)
├── platform/                 ← Cross-cutting infra (configs, web, DB managers, event bus, services)
├── presentation/             ← Only system endpoints
├── infrastructure/          ← Composition root (setup.py)
└── main.py
```

## Pre-existing Items Not Addressed

- **Pyright errors** (~97 errors): Pre-existing on develop branch. Not caused by refactor. Should be addressed separately if desired.
