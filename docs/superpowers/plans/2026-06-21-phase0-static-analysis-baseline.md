# Phase 0: Static Analysis Baseline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the architectural-rules safety net (`import-linter` + pre-commit hook + `make arch-check`) on the **current** layer-first architecture, snapshot baseline metrics, and prepare the refactor branch — all without touching application code.

**Architecture:** Add `import-linter` as a project dependency, configure it in `pyproject.toml` with contracts that reflect the *current* layer boundaries (presentation → application → domain, plus "domain may not import infrastructure"). Wire it into `make arch-check` and pre-commit. Run the full test suite and record test count + coverage as the baseline to beat after each refactor phase.

**Tech Stack:** `import-linter >= 2.0`, Poetry, Docker-first Makefile, pre-commit, pytest with coverage.

**Reference spec:** `docs/superpowers/specs/2026-06-21-bc-modular-monolith-refactor-design.md` §7 (Architectural Rules Enforcement), §8 Phase 0.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `pyproject.toml` | Modify (1 location: add dep; 1 location: add `[tool.importlinter]` section) | Declare dependency + contracts |
| `makefiles/quality.mk` | Modify (add `arch-check` target + update `check` target) | Expose `make arch-check` |
| `.pre-commit-config.yaml` | Modify (add `import-linter` hook) | Block bad imports at commit time |
| `docs/superpowers/specs/refactor-baseline.md` | Create | Record test count + coverage snapshot |
| `app/__init__.py` | Verify exists (no change) | Needed so `root_packages = ["app"]` resolves |

No application code is touched in this phase.

---

## Task 1: Add `import-linter` dependency

**Files:**
- Modify: `pyproject.toml` (the `[tool.poetry.group.dev.dependencies]` section)

- [ ] **Step 1: Add the dependency via Poetry**

Run inside Docker (per CLAUDE.md "Docker-first"):

```bash
make shell
```

Then inside the container:

```bash
poetry add --group dev "import-linter>=2.0,<3.0"
exit
```

This updates `pyproject.toml` and `poetry.lock`. If `make shell` is unavailable or you prefer a one-liner from the host:

```bash
docker-compose exec -T python poetry add --group dev "import-linter>=2.0,<3.0"
```

- [ ] **Step 2: Verify the dependency was added**

Read `pyproject.toml` and confirm the `[tool.poetry.group.dev.dependencies]` section now contains:

```toml
import-linter = ">=2.0,<3.0"
```

- [ ] **Step 3: Verify `lint-imports` is runnable**

```bash
docker-compose exec -T python poetry run lint-imports --version
```

Expected: a version string like `lint-imports 2.x` (no traceback).

- [ ] **Step 4: Commit the dependency change**

```bash
git add pyproject.toml poetry.lock
git commit -m "chore: add import-linter for architectural rule enforcement"
```

---

## Task 2: Configure `import-linter` with current-architecture contracts

These contracts describe the **current** layer-first architecture. They must pass on the first run (the codebase already obeys them). Later phases will tighten and replace them.

**Files:**
- Modify: `pyproject.toml` (append a new top-level `[tool.importlinter]` section at the end of the file)

- [ ] **Step 1: Append the `[tool.importlinter]` section**

Open `pyproject.toml` and add the following at the very end of the file (do not modify any existing content):

```toml

# =============================================================================
# import-linter — Architectural rule enforcement
# =============================================================================
# These contracts describe the CURRENT (layer-first) architecture.
# They will be replaced by Bounded-Context contracts during the refactor
# (see docs/superpowers/specs/2026-06-21-bc-modular-monolith-refactor-design.md).
[tool.importlinter]
root_packages = ["app"]

# Contract A: Presentation depends on Application, not the other way around.
# Contract B: Domain has zero infrastructure / framework imports.
[[tool.importlinter.contracts]]
name = "Layer boundaries (current architecture)"
type = "layers"
layers = [
    "app.presentation",
    "app.core.application",
    "app.core.domain",
]
# Note: app.infrastructure is intentionally NOT in this layers contract
# because it legitimately imports from app.core.domain (dependency inversion
# via Protocol implementations). The forbidden contract below enforces the
# reverse direction.

[[tool.importlinter.contracts]]
name = "Domain has no infrastructure or framework imports"
type = "forbidden"
source_modules = ["app.core.domain"]
forbidden_modules = [
    "app.infrastructure",
    "app.presentation",
    "fastapi",
    "sqlmodel",
    "sqlalchemy",
    "beanie",
    "motor",
]

[[tool.importlinter.contracts]]
name = "Domain has no application imports"
type = "forbidden"
source_modules = ["app.core.domain"]
forbidden_modules = ["app.core.application"]
```

**Why these contracts:**
- The `layers` contract ensures `presentation → application → domain` direction (each layer may only import the next inner one, never the reverse).
- The `forbidden` contract guarantees the domain layer stays pure (no FastAPI, no SQLModel, no SQLAlchemy, no Beanie, no Motor — matches `architecture.md` and AGENTS.md rule 12 spirit).
- The "domain has no application imports" contract is the dependency-inversion guarantee: domain never depends up.

- [ ] **Step 2: Run `lint-imports` to verify all contracts pass**

```bash
docker-compose exec -T python poetry run lint-imports
```

Expected output:

```
====
Discovered 3 contracts.
====
Name: Layer boundaries (current architecture)
    ✔ Kept.

Name: Domain has no infrastructure or framework imports
    ✔ Kept.

Name: Domain has no application imports
    ✔ Kept.

----
3/3 contracts KEPT.
```

If any contract fails: **STOP**. A failure means the current codebase already violates a rule that AGENTS.md claims to enforce. Do NOT weaken the contract to make it pass — instead fix the offending import (it is a real bug per the documented architecture). If you cannot fix it without changing behavior, surface the issue before proceeding.

- [ ] **Step 3: Commit the configuration**

```bash
git add pyproject.toml
git commit -m "chore: configure import-linter contracts for current architecture"
```

---

## Task 3: Add `make arch-check` target

**Files:**
- Modify: `makefiles/quality.mk` (add a new target after the type-check section, and update the `check` target)

- [ ] **Step 1: Add the `arch-check` target**

Open `makefiles/quality.mk`. Locate the "Type Checking" section (ends around line 37 with the `typecheck` target). Immediately after that section, and before the "Combined Commands" section, add a new section:

```makefile
# -----------------------------------------------------------------------------
# Architectural Rules
# -----------------------------------------------------------------------------
.PHONY: arch-check
arch-check: ## Verify architectural rules (import-linter contracts)
	@echo -e "$(YELLOW)Verifying architectural rules...$(RESET)"
	$(DOCKER_EXEC) poetry run lint-imports
```

- [ ] **Step 2: Update the `check` target to include `arch-check`**

In the same file, find the existing `check` target (in the "Combined Commands" section):

```makefile
.PHONY: check
check: format-check lint typecheck ## Run all code quality checks
	@echo -e "$(GREEN)All code quality checks completed!$(RESET)"
```

Change it to:

```makefile
.PHONY: check
check: format-check lint typecheck arch-check ## Run all code quality checks
	@echo -e "$(GREEN)All code quality checks completed!$(RESET)"
```

- [ ] **Step 3: Verify the new target works**

```bash
make arch-check
```

Expected: the same green output as `docker-compose exec -T python poetry run lint-imports` (3/3 contracts KEPT), prefixed with the "Verifying architectural rules..." line.

- [ ] **Step 4: Verify `make check` still works**

```bash
make check
```

Expected: format-check, lint, typecheck, and arch-check all pass. Any failure here is a pre-existing issue unrelated to this change — do not fix it in this phase, but report it.

- [ ] **Step 5: Commit**

```bash
git add makefiles/quality.mk
git commit -m "chore: add make arch-check target for import-linter"
```

---

## Task 4: Add `import-linter` pre-commit hook

**Files:**
- Modify: `.pre-commit-config.yaml` (append a new repo block)

- [ ] **Step 1: Add the hook**

Open `.pre-commit-config.yaml`. The current contents end after the ruff block. Append the following block at the end:

```yaml
  - repo: local
    hooks:
      - id: import-linter
        name: import-linter (architectural rules)
        entry: poetry run lint-imports
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
```

**Why `repo: local` + `language: system`:** `import-linter` is already installed by Poetry in the project venv. A local system hook reuses that installation instead of creating a separate isolated environment (which would download dependencies again and be slow). `pass_filenames: false` + `always_run: true` are required because `lint-imports` reads the whole project graph, not individual staged files.

- [ ] **Step 2: Verify the hook works**

Stage a trivial change so pre-commit runs:

```bash
# Touch an existing file to create a change
touch app/main.py
git add app/main.py
git commit -m "test: trigger pre-commit to verify import-linter hook" --allow-empty
# Reset the test commit if it succeeded
git reset --soft HEAD~1
git restore --staged app/main.py
```

Expected: the commit attempt runs all hooks including the new `import-linter` one. The hook should pass (green). If it fails, fix the configuration — do NOT bypass the hook.

If you used `--allow-empty` there may be nothing to commit; in that case just run:

```bash
docker-compose exec -T python poetry run pre-commit run import-linter --all-files
```

Expected: `import-linter (architectural rules)...............................Passed`.

- [ ] **Step 3: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: add import-linter pre-commit hook"
```

---

## Task 5: Snapshot baseline metrics

**Files:**
- Create: `docs/superpowers/specs/refactor-baseline.md`

- [ ] **Step 1: Run the full test suite with coverage**

```bash
make test-all-cov
```

Wait for it to complete. Capture from the terminal:
- The total number of tests collected and passed.
- The overall coverage percentage (the `TOTAL` row of the coverage table).

- [ ] **Step 2: Capture an endpoint inventory (smoke-test target)**

Run from the host (with the app up via `make dev` or `make up`):

```bash
curl -sf http://localhost:8080/openapi.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join(sorted(f'{m.upper():7} {p}' for p,ops in d['paths'].items() for m in ops)))"
```

Capture the full list of endpoints. This is the contract that must not shrink during the refactor.

If the app is not running, start it first:

```bash
make up
# wait ~10s for it to be ready
```

- [ ] **Step 3: Write the baseline document**

Create `docs/superpowers/specs/refactor-baseline.md` with this exact structure (fill in the bracketed values with what you captured):

```markdown
# Refactor Baseline Metrics

- **Captured:** 2026-06-21
- **Branch:** `refactor/bc-modular-monolith`
- **Commit at capture:** `<run: git rev-parse HEAD>`

## Purpose

These numbers are the **minimum acceptable** after each refactor phase. If any phase produces fewer tests, lower coverage, or fewer endpoints, that phase is incomplete.

## Tests

- **Total tests collected:** `<N>`
- **Total tests passed:** `<N>`
- **Total tests failed:** 0
- **Unit tests:** `<N>` (in `tests/unit/`)
- **Integration tests:** `<N>` (in `tests/integration/`)
- **E2E tests:** `<N>` (in `tests/e2e/`)

## Coverage

- **Overall:** `<NN>%`
- **app/core/domain:** `<NN>%`
- **app/core/application:** `<NN>%`
- **app/presentation:** `<NN>%`
- **app/infrastructure:** `<NN>%`

## Endpoints (must not shrink)

```
<paste the full curl output here — one METHOD path per line>
```

## Architecture check

- `make arch-check` status at capture: **GREEN** (3/3 contracts kept)
```

- [ ] **Step 4: Commit the baseline**

```bash
git add docs/superpowers/specs/refactor-baseline.md
git commit -m "docs: snapshot refactor baseline metrics (tests, coverage, endpoints)"
```

---

## Task 6: Phase 0 verification (Definition of Done)

This task verifies that Phase 0 is complete per the spec's DoD. No files are modified — this is a checklist run.

- [ ] **Step 1: Verify `import-linter` is installed and configured**

```bash
docker-compose exec -T python poetry run lint-imports
```

Expected: `3/3 contracts KEPT`.

- [ ] **Step 2: Verify `make arch-check` works**

```bash
make arch-check
```

Expected: green, "Verifying architectural rules..." + "3/3 contracts KEPT".

- [ ] **Step 3: Verify pre-commit hook is installed**

```bash
docker-compose exec -T python poetry run pre-commit run import-linter --all-files
```

Expected: `Passed`.

- [ ] **Step 4: Verify tests are still green**

```bash
make test-all
```

Expected: all tests pass, 0 failures.

- [ ] **Step 5: Verify the app still runs**

```bash
make up
# wait ~10s
curl -sf http://localhost:8080/health-check
```

Expected: JSON response with `"status": "healthy"` (or similar). Then:

```bash
make down
```

- [ ] **Step 6: Verify baseline document exists and is committed**

```bash
ls docs/superpowers/specs/refactor-baseline.md
git log --oneline -1 -- docs/superpowers/specs/refactor-baseline.md
```

Expected: the file exists and shows in a `docs:` commit.

- [ ] **Step 7: Verify git history is clean**

```bash
git log --oneline main..HEAD
```

Expected: roughly 5 commits on this branch (dependency, config, makefile, pre-commit, baseline), each with a clear conventional-commit message.

If any step above fails, do not declare Phase 0 done — fix the issue first.

---

## Phase 0 Complete — Hand-off

Once all 6 tasks above are checked off:

1. Do **not** merge to main yet. Phase 1 will build on top of this branch.
2. The next plan (`2026-06-21-phase1-shared-kernel-platform.md`) will be written against the HEAD of this branch.
3. The baseline metrics in `docs/superpowers/specs/refactor-baseline.md` become the acceptance bar for all subsequent phases.

**Acceptance criteria for Phase 0 (from spec §8):**
- [x] `import-linter` installed and configured
- [x] `make arch-check` target exists and passes
- [x] pre-commit hook installed and passes
- [x] `make test-all` green
- [x] `make dev`/`make up` runs the app
- [x] Baseline metrics committed to `docs/superpowers/specs/refactor-baseline.md`
