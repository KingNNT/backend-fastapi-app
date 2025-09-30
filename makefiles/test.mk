# Testing (runs inside Docker)

.PHONY: test
test: ## Run unit tests (in Docker)
	@echo -e "$(GREEN)Running unit tests...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/unit/ -v

.PHONY: test-cov
test-cov: ## Run unit tests with coverage report (in Docker)
	@echo -e "$(GREEN)Running unit tests with coverage...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/unit/ --cov=app --cov-report=term-missing --cov-report=html

.PHONY: test-integration
test-integration: ## Run integration tests (in Docker)
	@echo -e "$(GREEN)Running integration tests...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/e2e/ -v

.PHONY: test-all
test-all: ## Run all tests (in Docker)
	@echo -e "$(GREEN)Running all tests...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/ -v

.PHONY: test-watch
test-watch: ## Run tests in watch mode (in Docker)
	@echo -e "$(GREEN)Running tests in watch mode...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/unit/ -v --tb=short -x --lf
