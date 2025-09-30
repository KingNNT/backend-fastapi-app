# Code Quality (runs inside Docker)

.PHONY: format
format: ## Format code with ruff (in Docker)
	@echo -e "$(GREEN)Formatting code with ruff...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff format

.PHONY: format-check
format-check: ## Check code formatting (in Docker)
	@echo -e "$(YELLOW)Checking code formatting...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff format --check

.PHONY: lint
lint: ## Run linting with ruff (in Docker)
	@echo -e "$(YELLOW)Running ruff linter...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff check

.PHONY: lint-fix
lint-fix: ## Run linting with auto-fix (in Docker)
	@echo -e "$(GREEN)Running ruff linter with auto-fix...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff check --fix

.PHONY: typecheck
typecheck: ## Run type checking with pyright (in Docker)
	@echo -e "$(YELLOW)Running type checking with pyright...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pyright

.PHONY: check
check: format-check lint typecheck ## Run all code quality checks (in Docker)
	@echo -e "$(GREEN)All code quality checks completed!$(RESET)"

.PHONY: fix
fix: format lint-fix ## Format and fix all code issues (in Docker)
	@echo -e "$(GREEN)Code formatting and linting completed!$(RESET)"
