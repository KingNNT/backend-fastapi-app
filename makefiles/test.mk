# =============================================================================
# Testing (runs inside Docker)
# =============================================================================

# -----------------------------------------------------------------------------
# Unit Tests
# -----------------------------------------------------------------------------
.PHONY: test
test: ## Run unit tests
	@echo -e "$(GREEN)Running unit tests...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/unit/ -v

.PHONY: test-cov
test-cov: ## Run unit tests with coverage report
	@echo -e "$(GREEN)Running unit tests with coverage...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/unit/ --cov=app --cov-report=term-missing --cov-report=html

.PHONY: test-watch
test-watch: ## Run tests in watch mode (rerun on changes)
	@echo -e "$(GREEN)Running tests in watch mode...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/unit/ -v --tb=short -x --lf

# -----------------------------------------------------------------------------
# Integration & E2E Tests
# -----------------------------------------------------------------------------
.PHONY: test-integration
test-integration: ## Run integration tests (uses testcontainers)
	@echo -e "$(GREEN)Running integration tests...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/integration/ -v -m integration

.PHONY: test-e2e
test-e2e: ## Run E2E tests (uses test databases)
	@echo -e "$(GREEN)Running E2E tests with test databases...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/e2e/ -v -m e2e

# -----------------------------------------------------------------------------
# All Tests
# -----------------------------------------------------------------------------
.PHONY: test-all
test-all: ## Run all tests (unit + integration + e2e)
	@echo -e "$(GREEN)Running all tests...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/unit/ tests/e2e/ tests/integration/ -v

.PHONY: test-all-cov
test-all-cov: ## Run all tests with coverage
	@echo -e "$(GREEN)Running all tests with coverage...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/unit/ tests/e2e/ tests/integration/ --cov=app --cov-report=term-missing --cov-report=html

# -----------------------------------------------------------------------------
# Selective Testing
# -----------------------------------------------------------------------------
.PHONY: test-file
test-file: ## Run tests for a specific file (usage: make test-file FILE=tests/unit/test_user.py)
ifndef FILE
	@echo -e "$(RED)Error: FILE is required$(RESET)"
	@echo -e "Usage: make test-file FILE=tests/unit/test_user.py"
	@exit 1
endif
	@echo -e "$(GREEN)Running tests for $(FILE)...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest $(FILE) -v

.PHONY: test-match
test-match: ## Run tests matching pattern (usage: make test-match PATTERN="test_create")
ifndef PATTERN
	@echo -e "$(RED)Error: PATTERN is required$(RESET)"
	@echo -e "Usage: make test-match PATTERN=\"test_create\""
	@exit 1
endif
	@echo -e "$(GREEN)Running tests matching '$(PATTERN)'...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/ -v -k "$(PATTERN)"

.PHONY: test-failed
test-failed: ## Rerun only failed tests
	@echo -e "$(YELLOW)Rerunning failed tests...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/ -v --lf

.PHONY: test-failed-first
test-failed-first: ## Run failed tests first, then all
	@echo -e "$(YELLOW)Running failed tests first...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/ -v --ff

# -----------------------------------------------------------------------------
# Test Utilities
# -----------------------------------------------------------------------------
.PHONY: test-debug
test-debug: ## Run tests with debug output (no capture)
	@echo -e "$(GREEN)Running tests with debug output...$(RESET)"
	$(DOCKER_EXEC) poetry run pytest tests/unit/ -v -s --tb=long

.PHONY: test-markers
test-markers: ## Show available test markers
	@echo -e "$(CYAN)Available test markers:$(RESET)"
	$(DOCKER_EXEC) poetry run pytest --markers
