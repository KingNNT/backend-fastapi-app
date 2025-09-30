# Docker Environment Management

.PHONY: build
build: ## Build docker images
	@echo -e "$(GREEN)Building docker images...$(RESET)"
	$(DOCKER_COMPOSE_DEV) build

.PHONY: start
start: ## Start all services (alias for up)
	@echo -e "$(GREEN)Starting development services...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up -d

.PHONY: stop
stop: ## Stop all services (alias for down)
	@echo -e "$(YELLOW)Stopping all services...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down

.PHONY: up
up: ## Start all services (development)
	@echo -e "$(GREEN)Starting development services...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up -d

.PHONY: up-logs
up-logs: ## Start all services with logs (development)
	@echo -e "$(GREEN)Starting development services with logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up

.PHONY: down
down: ## Stop all services
	@echo -e "$(YELLOW)Stopping all services...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down

.PHONY: restart
restart: down up ## Restart all services
	@echo -e "$(GREEN)Services restarted!$(RESET)"

.PHONY: rebuild
rebuild: down build up ## Rebuild and restart all services
	@echo -e "$(GREEN)Services rebuilt and restarted!$(RESET)"

.PHONY: status
status: ## Show services status
	@echo -e "$(GREEN)Services status:$(RESET)"
	$(DOCKER_COMPOSE_DEV) ps

# Production Commands
.PHONY: prod-build
prod-build: ## Build production images
	@echo -e "$(GREEN)Building production images...$(RESET)"
	$(DOCKER_COMPOSE_PROD) build

.PHONY: prod-up
prod-up: ## Start production services
	@echo -e "$(GREEN)Starting production services...$(RESET)"
	$(DOCKER_COMPOSE_PROD) up -d

.PHONY: prod-down
prod-down: ## Stop production services
	@echo -e "$(YELLOW)Stopping production services...$(RESET)"
	$(DOCKER_COMPOSE_PROD) down

.PHONY: prod-logs
prod-logs: ## Show production logs
	@echo -e "$(GREEN)Showing production logs...$(RESET)"
	$(DOCKER_COMPOSE_PROD) logs -f
