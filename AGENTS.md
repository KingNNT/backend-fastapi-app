# AGENTS Guidelines

## Project Overview

This is a **Bounded Context (BC) Modular Monolith** built with **DDD tactical patterns + CQRS + Unit of Work**. The codebase is organized around Bounded Contexts (currently `iam/` and `audit/`) as the primary architectural axis. Each BC owns its full stack: domain, application, infrastructure, presentation.

Full architecture documentation: see `docs/architecture.md`.

## Development Workflow

1. Operate Docker-first; never run poetry/pytest directly on host.
2. Spin services with `make dev`/`make up`; rebuild via `make build` or `make rebuild`; down using `make down`.
3. Format code with `make format`; check formatting using `make format-check`.
4. Run Ruff linting with `make lint`; auto-fix via `make lint-fix`.
5. Type check through `make typecheck`; bundle checks with `make check`.
6. Run architectural rules with `make arch-check` (import-linter).
7. Execute unit tests using `make test`; coverage with `make test-cov`.
8. Per-BC tests: `make test-iam`, `make test-audit`.
9. Integration suite runs with `make test-integration`; all tests via `make test-all`.
10. CI smoke via `make ci`; watch mode available at `make test-watch`.
11. Single test flow: `make shell` → `poetry run pytest tests/path::test_name -v`.

## Architectural Rules (ENFORCED by `import-linter`)

The architectural rules below are NOT just conventions — they are enforced by `pyproject.toml`'s `[tool.importlinter]` section. CI will fail if any are violated. Always run `make arch-check` before committing.

12. **Bounded Context isolation**: BCs are FORBIDDEN from importing each other. The IAM BC and audit BC must remain fully decoupled.
   - Contract: `IAM does not import from audit BC` (forbidden)
   - Contract: `Audit does not import from iam BC` (forbidden, with one exception: the cross-BC event translator in `app/audit/infrastructure/event_handlers/iam_event_translator.py` is allowed to import IAM event types)

13. **Per-BC layer boundaries**: Within each BC, respect the strict direction: `presentation → application → domain ← infrastructure`.
   - Contract: `IAM layer boundaries` (layers: presentation, application, domain)
   - Contract: `Audit layer boundaries` (layers: presentation, application, domain)

14. **Domain purity**: Domain layer has zero infrastructure or framework imports. No `fastapi`, `sqlmodel`, `sqlalchemy`, `beanie`, `motor`, `pymongo`, or `app.iam.infrastructure` / `app.audit.infrastructure` in any `domain/` folder.
   - Contract: `IAM domain has no infrastructure or framework imports` (forbidden)
   - Contract: `Audit domain has no infrastructure or framework imports` (forbidden)

15. **Shared kernel purity**: `app/shared/` contains ONLY cross-BC contracts (base classes, ID VOs, bus interfaces, base UoW protocol). It must NOT import from any BC, platform, or presentation.
   - Contract: `Shared kernel is dependency-free` (forbidden)

16. **Platform isolation**: `app/platform/` (configs, web, DB managers, event bus, services) is BC-agnostic. It must NOT import BC domain or application code.
   - Contract: `Platform cannot import BC domain/application code` (forbidden)
   - Exception: `app/platform/web/exception_handlers.py` may import IAM exception types to translate them to HTTP responses (this will be cleaned up in a future refactor).

17. **Composition root is unique**: `app/infrastructure/setup.py` is the ONLY file allowed to import from multiple BCs. It wires cross-BC dependencies (event bus subscriptions, repository bindings).

18. **Cross-BC communication**: BCs MUST communicate via domain events on the `IEventBus`. Never import another BC's types directly in handler or domain code.

## Code Style

19. Follow Ruff defaults (PEP 8, 4-space indents, trailing commas encouraged).
20. Annotate functions with modern typing (`list[T]`, `Type | None`, dataclass models).
21. Keep async flows truly async; avoid blocking I/O in services or repositories.
22. Use `datetime.now(timezone.utc)` for timestamps; never `datetime.utcnow()`.
23. Initialize loggers via `logging.getLogger(__name__)`; no print statements.
24. Domain raises domain exceptions; presentation translates via handlers/`APIResponse`.
25. Use dependency injection via FastAPI Depends and setter functions.
26. DTOs and models extend project base classes and maintain audit fields.

## Adding a New Bounded Context

To add a new BC (e.g., `billing`):

1. **Create folder structure** mirroring `iam/` or `audit/`:
   ```
   app/billing/
   ├── domain/<aggregate>/
   ├── application/{commands,queries,handlers,read_models,interfaces}/
   ├── infrastructure/persistence/<db>/
   └── presentation/{api,dependencies,dtos}/
   ```

2. **Define `<BC>UnitOfWork`** in `app/billing/application/interfaces/unit_of_work.py`:
   ```python
   from app.shared.application.interfaces.unit_of_work import IUnitOfWork
   from app.billing.domain.invoice.repository import IInvoiceWriteRepository

   class IBillingUnitOfWork(IUnitOfWork, Protocol):
       invoices: IInvoiceWriteRepository
       # ... BC-specific repos
   ```

3. **Implement the UoW** in `app/billing/infrastructure/persistence/<db>/unit_of_work.py`.

4. **Add `app/billing` router** to `app/main.py`:
   ```python
   from app.billing.presentation.api import router as billing_router
   app.include_router(billing_router, prefix="/v1")
   ```

5. **Add `import-linter` contracts** in `pyproject.toml`:
   - `<BC> layer boundaries`
   - `<BC> domain has no infrastructure or framework imports`
   - `<BC> does not import from iam/audit` (for each pair)

6. **Add cross-BC subscriptions** in `app/infrastructure/setup.py` (if the new BC needs to consume events from other BCs).

7. **Mirror test structure** in `tests/<bc>/`:
   - `tests/<bc>/unit/`
   - `tests/<bc>/integration/`
   - `tests/<bc>/e2e/`

8. **Add Makefile target** in `makefiles/test.mk`:
   ```makefile
   test-billing: ## Run Billing tests only
   	$(DOCKER_EXEC) poetry run pytest tests/billing/ -v
   ```

## Quick Reference

| Task | Command |
|---|---|
| Run all checks | `make check` |
| Run arch rules only | `make arch-check` |
| Run all tests | `make test-all` |
| Run tests for one BC | `make test-iam` (or `test-audit`) |
| Format code | `make format` |
| Auto-fix lint | `make lint-fix` |
| Access container shell | `make shell` |
