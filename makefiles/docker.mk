# =============================================================================
# Docker Environment Management
# =============================================================================

# -----------------------------------------------------------------------------
# Development Commands
# -----------------------------------------------------------------------------
.PHONY: build
build: ## Build Docker images
	$(call check_docker)
	@echo -e "$(GREEN)Building Docker images...$(RESET)"
	$(DOCKER_COMPOSE) build

.PHONY: up
up: ## Start all services (detached)
	$(call check_docker)
	@echo -e "$(GREEN)Starting development services...$(RESET)"
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down: ## Stop all services
	@echo -e "$(YELLOW)Stopping all services...$(RESET)"
	$(DOCKER_COMPOSE) down

.PHONY: restart
restart: ## Restart all services
	@echo -e "$(YELLOW)Restarting services...$(RESET)"
	$(DOCKER_COMPOSE) restart
	@echo -e "$(GREEN)Services restarted!$(RESET)"

.PHONY: rebuild
rebuild: down build up ## Rebuild and restart all services
	@echo -e "$(GREEN)Services rebuilt and restarted!$(RESET)"

.PHONY: up-logs
up-logs: ## Start all services with logs (foreground)
	$(call check_docker)
	@echo -e "$(GREEN)Starting development services with logs...$(RESET)"
	$(DOCKER_COMPOSE) up

.PHONY: status
status: ## Show services status
	@echo -e "$(CYAN)Services status:$(RESET)"
	@$(DOCKER_COMPOSE) ps

.PHONY: logs
logs: ## Show application logs (follow mode)
	@echo -e "$(GREEN)Showing application logs...$(RESET)"
	$(DOCKER_COMPOSE) logs -f $(PYTHON_SERVICE)

.PHONY: logs-all
logs-all: ## Show all services logs (follow mode)
	@echo -e "$(GREEN)Showing all services logs...$(RESET)"
	$(DOCKER_COMPOSE) logs -f

# -----------------------------------------------------------------------------
# Production Commands
# -----------------------------------------------------------------------------
.PHONY: prod-build
prod-build: ## Build production images
	$(call check_docker)
	@echo -e "$(GREEN)Building production images...$(RESET)"
	$(DOCKER_COMPOSE_PROD) build

.PHONY: prod-up
prod-up: ## Start production services
	$(call check_docker)
	@echo -e "$(GREEN)Starting production services...$(RESET)"
	$(DOCKER_COMPOSE_PROD) up -d

.PHONY: prod-down
prod-down: ## Stop production services
	@echo -e "$(YELLOW)Stopping production services...$(RESET)"
	$(DOCKER_COMPOSE_PROD) down

.PHONY: prod-restart
prod-restart: ## Restart production services
	@echo -e "$(YELLOW)Restarting production services...$(RESET)"
	$(DOCKER_COMPOSE_PROD) restart
	@echo -e "$(GREEN)Production services restarted!$(RESET)"

.PHONY: prod-rebuild
prod-rebuild: prod-down prod-build prod-up ## Rebuild and restart production services
	@echo -e "$(GREEN)Production services rebuilt and restarted!$(RESET)"

.PHONY: prod-status
prod-status: ## Show production services status
	@echo -e "$(CYAN)Production services status:$(RESET)"
	@$(DOCKER_COMPOSE_PROD) ps

.PHONY: prod-logs
prod-logs: ## Show production logs (follow mode)
	@echo -e "$(GREEN)Showing production logs...$(RESET)"
	$(DOCKER_COMPOSE_PROD) logs -f

# -----------------------------------------------------------------------------
# Aliases (for convenience)
# -----------------------------------------------------------------------------
.PHONY: start
start: up ## Alias for 'up'

.PHONY: stop
stop: down ## Alias for 'down'
