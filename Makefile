# Makefile for backend-fastapi-app (Docker-first)

# Default shell
SHELL := /bin/bash

# Docker compose configuration
DOCKER_COMPOSE_DEV := docker-compose -f docker-compose.development.yaml
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.production.yaml
APP_CONTAINER := backend-fastapi-app-server_python

# Colors for output
BOLD := \033[1m
RESET := \033[0m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BLUE := \033[34m

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "$(BOLD)FastAPI Backend Commands (Docker-first)$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'

# Environment Setup
.PHONY: build
build: ## Build docker images
	@echo "$(GREEN)Building docker images...$(RESET)"
	$(DOCKER_COMPOSE_DEV) build

.PHONY: up
up: ## Start all services (development)
	@echo "$(GREEN)Starting development services...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up -d

.PHONY: up-logs
up-logs: ## Start all services with logs (development)
	@echo "$(GREEN)Starting development services with logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up

.PHONY: down
down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down

.PHONY: restart
restart: down up ## Restart all services
	@echo "$(GREEN)Services restarted!$(RESET)"

.PHONY: rebuild
rebuild: down build up ## Rebuild and restart all services
	@echo "$(GREEN)Services rebuilt and restarted!$(RESET)"

# Code Quality (runs inside Docker)
.PHONY: format
format: ## Format code with ruff (in Docker)
	@echo "$(GREEN)Formatting code with ruff...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff format

.PHONY: format-check
format-check: ## Check code formatting (in Docker)
	@echo "$(YELLOW)Checking code formatting...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff format --check

.PHONY: lint
lint: ## Run linting with ruff (in Docker)
	@echo "$(YELLOW)Running ruff linter...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff check

.PHONY: lint-fix
lint-fix: ## Run linting with auto-fix (in Docker)
	@echo "$(GREEN)Running ruff linter with auto-fix...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run ruff check --fix

.PHONY: check
check: format-check lint ## Run all code quality checks (in Docker)
	@echo "$(GREEN)All code quality checks completed!$(RESET)"

.PHONY: fix
fix: format lint-fix ## Format and fix all code issues (in Docker)
	@echo "$(GREEN)Code formatting and linting completed!$(RESET)"

# Testing (runs inside Docker)
.PHONY: test
test: ## Run unit tests (in Docker)
	@echo "$(GREEN)Running unit tests...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/unit/ -v

.PHONY: test-cov
test-cov: ## Run unit tests with coverage report (in Docker)
	@echo "$(GREEN)Running unit tests with coverage...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/unit/ --cov=app --cov-report=term-missing --cov-report=html

.PHONY: test-integration
test-integration: ## Run integration tests (in Docker)
	@echo "$(GREEN)Running integration tests...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/e2e/ -v

.PHONY: test-all
test-all: ## Run all tests (in Docker)
	@echo "$(GREEN)Running all tests...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/ -v

.PHONY: test-watch
test-watch: ## Run tests in watch mode (in Docker)
	@echo "$(GREEN)Running tests in watch mode...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run pytest app/tests/unit/ -v --tb=short -x --lf

# Installation and Dependencies (in Docker)
.PHONY: install
install: ## Install dependencies (in Docker)
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry install --no-root

.PHONY: install-dev
install-dev: ## Install dependencies including dev tools (in Docker)
	@echo "$(GREEN)Installing dependencies with dev tools...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry install --no-root --with dev

.PHONY: update
update: ## Update dependencies (in Docker)
	@echo "$(GREEN)Updating dependencies...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry update

# Shell Access
.PHONY: shell
shell: ## Access Python container shell
	@echo "$(GREEN)Accessing Python container shell...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python bash

.PHONY: shell-python
shell-python: ## Access Python REPL (in Docker)
	@echo "$(GREEN)Accessing Python REPL...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python python

.PHONY: shell-mongo
shell-mongo: ## Access MongoDB shell
	@echo "$(GREEN)Accessing MongoDB shell...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec mongodb mongosh

# Logs and Monitoring
.PHONY: logs
logs: ## Show application logs
	@echo "$(GREEN)Showing application logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) logs -f python

.PHONY: logs-db
logs-db: ## Show MongoDB logs
	@echo "$(GREEN)Showing MongoDB logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) logs -f mongodb

.PHONY: logs-all
logs-all: ## Show all services logs
	@echo "$(GREEN)Showing all services logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) logs -f

.PHONY: status
status: ## Show services status
	@echo "$(GREEN)Services status:$(RESET)"
	$(DOCKER_COMPOSE_DEV) ps

# Database Management
.PHONY: db-up
db-up: ## Start only MongoDB
	@echo "$(GREEN)Starting MongoDB...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up -d mongodb

.PHONY: db-down
db-down: ## Stop MongoDB
	@echo "$(YELLOW)Stopping MongoDB...$(RESET)"
	$(DOCKER_COMPOSE_DEV) stop mongodb

.PHONY: db-reset
db-reset: ## Reset MongoDB data (WARNING: deletes all data)
	@echo "$(RED)Resetting MongoDB data...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down mongodb
	docker volume rm backend-fastapi-app_mongodb_data || true
	$(DOCKER_COMPOSE_DEV) up -d mongodb

# Production Commands
.PHONY: prod-build
prod-build: ## Build production images
	@echo "$(GREEN)Building production images...$(RESET)"
	$(DOCKER_COMPOSE_PROD) build

.PHONY: prod-up
prod-up: ## Start production services
	@echo "$(GREEN)Starting production services...$(RESET)"
	$(DOCKER_COMPOSE_PROD) up -d

.PHONY: prod-down
prod-down: ## Stop production services
	@echo "$(YELLOW)Stopping production services...$(RESET)"
	$(DOCKER_COMPOSE_PROD) down

.PHONY: prod-logs
prod-logs: ## Show production logs
	@echo "$(GREEN)Showing production logs...$(RESET)"
	$(DOCKER_COMPOSE_PROD) logs -f

# Cleanup
.PHONY: clean
clean: ## Clean Docker containers and images
	@echo "$(YELLOW)Cleaning Docker containers and images...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down --rmi local --volumes --remove-orphans
	docker system prune -f

.PHONY: clean-all
clean-all: ## Deep clean Docker (WARNING: removes all containers, images, volumes)
	@echo "$(RED)Deep cleaning Docker...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down --rmi all --volumes --remove-orphans
	$(DOCKER_COMPOSE_PROD) down --rmi all --volumes --remove-orphans
	docker system prune -a -f --volumes

.PHONY: clean-cache
clean-cache: ## Clean Python cache files (in Docker)
	@echo "$(YELLOW)Cleaning Python cache files...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python find . -type f -name "*.pyc" -delete
	$(DOCKER_COMPOSE_DEV) exec python find . -type d -name "__pycache__" -delete
	$(DOCKER_COMPOSE_DEV) exec python find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Development Workflow
.PHONY: dev
dev: build up logs ## Full development setup (build, up, logs)

.PHONY: dev-reset
dev-reset: down clean-cache up ## Reset development environment

.PHONY: ci
ci: build up test-cov check ## Run CI pipeline (build, up, test with coverage, check)
	@echo "$(GREEN)CI pipeline completed successfully!$(RESET)"

.PHONY: verify
verify: ## Quick verification (ensure services are up, run checks and tests)
	@echo "$(GREEN)Verifying services...$(RESET)"
	@$(DOCKER_COMPOSE_DEV) ps
	@$(MAKE) check test
	@echo "$(GREEN)Verification completed successfully!$(RESET)"

# Health Checks
.PHONY: health
health: ## Check application health
	@echo "$(GREEN)Checking application health...$(RESET)"
	@curl -f http://localhost:8080/health-check || echo "$(RED)Health check failed$(RESET)"

.PHONY: ping-db
ping-db: ## Ping MongoDB
	@echo "$(GREEN)Pinging MongoDB...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec mongodb mongosh --eval "db.adminCommand('ping')"

# Utilities
.PHONY: version
version: ## Show application version (in Docker)
	@echo "$(BLUE)Application version:$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run python -c "from app.configs.version import get_app_version; print(get_app_version())"

.PHONY: docs
docs: ## Show API documentation URLs
	@echo "$(GREEN)API documentation available at: http://localhost:8080/docs$(RESET)"
	@echo "$(GREEN)ReDoc documentation available at: http://localhost:8080/redoc$(RESET)"
