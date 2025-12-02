# AGENTS Guidelines
1. Operate Docker-first; never run poetry/pytest directly on host.
2. Spin services with `make dev`/`make up`; rebuild via `make build` or `make rebuild`; down using `make down`.
3. Format code with `make format`; check formatting using `make format-check`.
4. Run Ruff linting with `make lint`; auto-fix via `make lint-fix`.
5. Type check through `make typecheck`; bundle checks with `make check`.
6. Execute unit tests using `make test`; coverage with `make test-cov`.
7. Integration suite runs with `make test-integration`; all tests via `make test-all`.
8. CI smoke via `make ci`; watch mode available at `make test-watch`.
9. Single test flow: `make shell` → `poetry run pytest app/tests/path::test_name -v`.
10. Respect barrel imports (`from app.internal.services import UserService`).
11. Keep layer boundaries router → service → repository → model → database.
12. Follow Ruff defaults (PEP 8, 4-space indents, trailing commas encouraged).
13. Annotate functions with modern typing (`list[T]`, `Type | None`, dataclass models).
14. Keep async flows truly async; avoid blocking I/O in services or repositories.
15. Use `datetime.now(timezone.utc)` for timestamps; never `datetime.utcnow()`.
16. Initialize loggers via `logging.getLogger(__name__)`; no print statements.
17. Services raise domain exceptions; routers translate via handlers/`APIResponse`.
18. Preserve singleton services and dependency providers (e.g., `get_user_service()`).
19. DTOs and models extend project base classes and maintain audit fields.
