# =============================================================================
# Code Quality (runs inside Docker)
# =============================================================================

# -----------------------------------------------------------------------------
# Formatting
# -----------------------------------------------------------------------------
.PHONY: format
format: ## Format code with ruff
	@echo -e "$(GREEN)Formatting code with ruff...$(RESET)"
	$(DOCKER_EXEC) poetry run ruff format

.PHONY: format-check
format-check: ## Check code formatting without changes
	@echo -e "$(YELLOW)Checking code formatting...$(RESET)"
	$(DOCKER_EXEC) poetry run ruff format --check

# -----------------------------------------------------------------------------
# Linting
# -----------------------------------------------------------------------------
.PHONY: lint
lint: ## Run linting with ruff
	@echo -e "$(YELLOW)Running ruff linter...$(RESET)"
	$(DOCKER_EXEC) poetry run ruff check

.PHONY: lint-fix
lint-fix: ## Run linting with auto-fix
	@echo -e "$(GREEN)Running ruff linter with auto-fix...$(RESET)"
	$(DOCKER_EXEC) poetry run ruff check --fix

# -----------------------------------------------------------------------------
# Type Checking
# -----------------------------------------------------------------------------
.PHONY: typecheck
typecheck: ## Run type checking with pyright
	@echo -e "$(YELLOW)Running type checking with pyright...$(RESET)"
	$(DOCKER_EXEC) poetry run pyright

# -----------------------------------------------------------------------------
# Combined Commands
# -----------------------------------------------------------------------------
.PHONY: check
check: format-check lint typecheck ## Run all code quality checks
	@echo -e "$(GREEN)All code quality checks completed!$(RESET)"

.PHONY: fix
fix: format lint-fix ## Format and fix all code issues
	@echo -e "$(GREEN)Code formatting and linting completed!$(RESET)"

# -----------------------------------------------------------------------------
# Pre-commit Hooks
# -----------------------------------------------------------------------------
.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo -e "$(GREEN)Installing pre-commit hooks...$(RESET)"
	$(DOCKER_EXEC) poetry run pre-commit install

.PHONY: pre-commit-run
pre-commit-run: ## Run pre-commit on all files
	@echo -e "$(YELLOW)Running pre-commit on all files...$(RESET)"
	$(DOCKER_EXEC) poetry run pre-commit run --all-files

.PHONY: pre-commit-update
pre-commit-update: ## Update pre-commit hooks
	@echo -e "$(GREEN)Updating pre-commit hooks...$(RESET)"
	$(DOCKER_EXEC) poetry run pre-commit autoupdate
