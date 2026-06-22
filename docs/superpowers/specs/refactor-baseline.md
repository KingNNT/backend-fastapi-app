# Refactor Baseline Metrics

- **Captured:** 2026-06-21
- **Branch:** `refactor/bc-modular-monolith`
- **Commit at capture:** `e4e068ea16a0d0fd7d929d5f20cf3b5b34aedcd3`

## Purpose

These numbers are the **minimum acceptable** after each refactor phase. If any phase produces fewer tests, lower coverage, or fewer endpoints, that phase is incomplete.

## Tests

- **Total tests collected:** 145
- **Total tests passed:** 145
- **Total tests failed:** 0
- **Unit tests:** 98 (in `tests/unit/`)
  - `tests/unit/domain/test_value_objects.py`: 31
  - `tests/unit/domain/test_entities.py`: 20
  - `tests/unit/domain/test_aggregates.py`: 21
  - `tests/unit/application/test_query_handlers.py`: 10
  - `tests/unit/application/test_command_handlers.py`: 16
- **Integration tests:** 30 (in `tests/integration/`)
  - `tests/integration/mongodb/test_log_repository.py`: 11
  - `tests/integration/event_handlers/test_user_events.py`: 7
  - `tests/integration/postgresql/test_user_repository.py`: 12
- **E2E tests:** 17 (in `tests/e2e/`)
  - `tests/e2e/test_user_api.py`: 17

## Coverage

- **Overall:** 66% (4214 statements, 1448 missing)

Per-layer approximate coverage (computed from the `--cov-report=term` output):

| Layer | Files | Coverage |
|---|---|---|
| `app/core/domain` | aggregates, entities, value_objects, events, services, repositories, specifications, exceptions | high (~90%+) |
| `app/core/application` | commands, queries, handlers, read_models, interfaces | moderate (~70%) |
| `app/presentation` | api, dependencies, dtos | moderate (~60%) |
| `app/infrastructure` | persistence, web, messaging, setup | low (~40%) |

> Exact per-directory percentages are not captured here to keep the baseline stable against file additions. The overall 66% is the acceptance bar.

## Endpoints (must not shrink)

30 endpoints total:

```
GET     /health-check
GET     /version
POST    /v1/users/
GET     /v1/users/
GET     /v1/users/{id}
PUT     /v1/users/{id}
DELETE  /v1/users/{id}
GET     /v1/users/by-email/{email}
GET     /v1/users/by-username/{username}
GET     /v1/users/{id}/roles
POST    /v1/users/{id}/roles
DELETE  /v1/users/{id}/roles/{role_id}
GET     /v1/users/{id}/permissions
POST    /v1/users/{id}/permissions
DELETE  /v1/users/{id}/permissions/{permission_id}
POST    /v1/roles/
GET     /v1/roles/
GET     /v1/roles/{id}
PUT     /v1/roles/{id}
DELETE  /v1/roles/{id}
GET     /v1/roles/{id}/permissions
POST    /v1/roles/{id}/permissions
DELETE  /v1/roles/{id}/permissions/{permission_id}
POST    /v1/permissions/
GET     /v1/permissions/
GET     /v1/permissions/{id}
PUT     /v1/permissions/{id}
DELETE  /v1/permissions/{id}
GET     /v1/logs/
GET     /v1/logs/{id}
```

## Architecture check

- `make arch-check` status at capture: **GREEN** (3/3 contracts kept)
- Contracts:
  1. Layer boundaries (current architecture) — KEPT
  2. Domain has no infrastructure or framework imports — KEPT
  3. Domain has no application imports — KEPT

## Known pre-existing issues (not caused by refactor)

- `make typecheck` (pyright): 97 errors, 65 warnings — these exist on `develop` before the refactor branch. They are **not** a blocker for Phase 0 but should be addressed separately.
