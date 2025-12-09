# =============================================================================
# Utilities and Shell Access
# =============================================================================

# -----------------------------------------------------------------------------
# Dependency Management
# -----------------------------------------------------------------------------
.PHONY: install
install: ## Install dependencies
	@echo -e "$(GREEN)Installing dependencies...$(RESET)"
	$(DOCKER_EXEC) poetry install --no-root

.PHONY: install-dev
install-dev: ## Install dependencies including dev tools
	@echo -e "$(GREEN)Installing dependencies with dev tools...$(RESET)"
	$(DOCKER_EXEC) poetry install --no-root --with dev

.PHONY: update
update: ## Update dependencies
	@echo -e "$(GREEN)Updating dependencies...$(RESET)"
	$(DOCKER_EXEC) poetry update

.PHONY: lock
lock: ## Update poetry.lock without installing
	@echo -e "$(GREEN)Updating poetry.lock...$(RESET)"
	$(DOCKER_EXEC) poetry lock

.PHONY: outdated
outdated: ## Show outdated dependencies
	@echo -e "$(CYAN)Checking for outdated dependencies...$(RESET)"
	$(DOCKER_EXEC) poetry show --outdated

# -----------------------------------------------------------------------------
# Shell Access
# -----------------------------------------------------------------------------
.PHONY: shell
shell: ## Access container bash shell
	@echo -e "$(GREEN)Accessing container shell...$(RESET)"
	$(DOCKER_COMPOSE) exec $(PYTHON_SERVICE) bash

.PHONY: shell-python
shell-python: ## Access Python REPL
	@echo -e "$(GREEN)Accessing Python REPL...$(RESET)"
	$(DOCKER_EXEC) python

.PHONY: shell-ipython
shell-ipython: ## Access IPython REPL (if installed)
	@echo -e "$(GREEN)Accessing IPython REPL...$(RESET)"
	$(DOCKER_EXEC) poetry run ipython

# -----------------------------------------------------------------------------
# Cleanup Commands
# -----------------------------------------------------------------------------
.PHONY: clean
clean: ## Clean Docker containers and local images
	@echo -e "$(YELLOW)Cleaning Docker containers and images...$(RESET)"
	$(DOCKER_COMPOSE) down --rmi local --remove-orphans
	@echo -e "$(GREEN)Cleanup completed!$(RESET)"

.PHONY: clean-volumes
clean-volumes: ## Clean Docker volumes (WARNING: deletes data)
	$(call confirm,WARNING: This will delete all Docker volumes!)
	@echo -e "$(RED)Cleaning Docker volumes...$(RESET)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo -e "$(GREEN)Volumes cleaned!$(RESET)"

.PHONY: clean-all
clean-all: ## Deep clean everything (WARNING: removes all containers, images, volumes)
	$(call confirm,WARNING: This will remove ALL Docker resources for this project!)
	@echo -e "$(RED)Deep cleaning Docker...$(RESET)"
	$(DOCKER_COMPOSE) down --rmi all -v --remove-orphans
	$(DOCKER_COMPOSE_PROD) down --rmi all -v --remove-orphans 2>/dev/null || true
	docker system prune -f
	@echo -e "$(GREEN)Deep cleanup completed!$(RESET)"

.PHONY: clean-cache
clean-cache: ## Clean Python cache files
	@echo -e "$(YELLOW)Cleaning Python cache files...$(RESET)"
	$(DOCKER_EXEC) find . -type f -name "*.pyc" -delete 2>/dev/null || true
	$(DOCKER_EXEC) find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	$(DOCKER_EXEC) find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	$(DOCKER_EXEC) find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	$(DOCKER_EXEC) find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo -e "$(GREEN)Cache cleaned!$(RESET)"

.PHONY: clean-coverage
clean-coverage: ## Clean coverage reports
	@echo -e "$(YELLOW)Cleaning coverage reports...$(RESET)"
	$(DOCKER_EXEC) rm -rf htmlcov .coverage coverage.xml 2>/dev/null || true
	@echo -e "$(GREEN)Coverage reports cleaned!$(RESET)"

# -----------------------------------------------------------------------------
# Health & Status
# -----------------------------------------------------------------------------
.PHONY: health
health: ## Check application health
	@echo -e "$(CYAN)Checking application health...$(RESET)"
	@curl -sf http://localhost:8080/health-check && echo -e "$(GREEN)Application is healthy!$(RESET)" || echo -e "$(RED)Health check failed!$(RESET)"

.PHONY: version
version: ## Show application version
	@echo -e "$(CYAN)Application version:$(RESET)"
	@$(DOCKER_EXEC) python -c "from app.infrastructure.configs import get_app_config; c = get_app_config(); print(f'{c.name} v{c.version}')" 2>/dev/null || echo "Unable to get version"

.PHONY: info
info: ## Show project information
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "$(BOLD)  Project Information$(RESET)"
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "  $(YELLOW)Project:$(RESET)     $(PROJECT_NAME)"
	@echo -e "  $(YELLOW)Python:$(RESET)      $(shell docker-compose exec -T $(PYTHON_SERVICE) python --version 2>/dev/null || echo 'N/A')"
	@echo -e "  $(YELLOW)Poetry:$(RESET)      $(shell docker-compose exec -T $(PYTHON_SERVICE) poetry --version 2>/dev/null || echo 'N/A')"
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"

# -----------------------------------------------------------------------------
# Documentation
# -----------------------------------------------------------------------------
.PHONY: docs
docs: ## Show API documentation URLs
	@echo -e "$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "$(BOLD)  API Documentation$(RESET)"
	@echo -e "$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "  $(GREEN)Swagger UI:$(RESET)  http://localhost:8080/docs"
	@echo -e "  $(GREEN)ReDoc:$(RESET)       http://localhost:8080/redoc"
	@echo -e "  $(GREEN)OpenAPI:$(RESET)     http://localhost:8080/openapi.json"
	@echo -e "$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"

.PHONY: open-docs
open-docs: ## Open API documentation in browser
	@echo -e "$(GREEN)Opening API documentation...$(RESET)"
	@open http://localhost:8080/docs 2>/dev/null || xdg-open http://localhost:8080/docs 2>/dev/null || echo "Please open http://localhost:8080/docs in your browser"
