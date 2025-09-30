# Utilities and Shell Access

# Installation and Dependencies
.PHONY: install
install: ## Install dependencies (in Docker)
	@echo -e "$(GREEN)Installing dependencies...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry install --no-root

.PHONY: install-dev
install-dev: ## Install dependencies including dev tools (in Docker)
	@echo -e "$(GREEN)Installing dependencies with dev tools...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry install --no-root --with dev

.PHONY: update
update: ## Update dependencies (in Docker)
	@echo -e "$(GREEN)Updating dependencies...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry update

# Shell Access
.PHONY: shell
shell: ## Access Python container shell
	@echo -e "$(GREEN)Accessing Python container shell...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python bash

.PHONY: shell-python
shell-python: ## Access Python REPL (in Docker)
	@echo -e "$(GREEN)Accessing Python REPL...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python python

# Logs and Monitoring
.PHONY: logs
logs: ## Show application logs
	@echo -e "$(GREEN)Showing application logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) logs -f python

.PHONY: logs-all
logs-all: ## Show all services logs
	@echo -e "$(GREEN)Showing all services logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) logs -f

# Cleanup
.PHONY: clean
clean: ## Clean Docker containers and images
	@echo -e "$(YELLOW)Cleaning Docker containers and images...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down --rmi local --volumes --remove-orphans
	docker system prune -f

.PHONY: clean-all
clean-all: ## Deep clean Docker (WARNING: removes all containers, images, volumes)
	@echo -e "$(RED)Deep cleaning Docker...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down --rmi all --volumes --remove-orphans
	$(DOCKER_COMPOSE_PROD) down --rmi all --volumes --remove-orphans
	docker system prune -a -f --volumes

.PHONY: clean-cache
clean-cache: ## Clean Python cache files (in Docker)
	@echo -e "$(YELLOW)Cleaning Python cache files...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python find . -type f -name "*.pyc" -delete
	$(DOCKER_COMPOSE_DEV) exec python find . -type d -name "__pycache__" -delete
	$(DOCKER_COMPOSE_DEV) exec python find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Health Checks
.PHONY: health
health: ## Check application health
	@echo -e "$(GREEN)Checking application health...$(RESET)"
	@curl -f http://localhost:8080/health-check || echo "$(RED)Health check failed$(RESET)"

# Version and Documentation
.PHONY: version
version: ## Show application version (in Docker)
	@echo -e "$(BLUE)Application version:$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run python -c "from app.configs.version import get_app_version; print(get_app_version())"

.PHONY: docs
docs: ## Show API documentation URLs
	@echo -e "$(GREEN)API documentation available at: http://localhost:8080/docs$(RESET)"
	@echo -e "$(GREEN)ReDoc documentation available at: http://localhost:8080/redoc$(RESET)"
