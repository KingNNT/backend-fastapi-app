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
	@echo -e "$(BOLD)FastAPI Backend Commands (Docker-first)$(RESET)"
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Docker & Environment:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/docker.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Code Quality:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/quality.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Testing:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/test.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Database Management:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/database.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Utilities & Tools:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/utils.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Development Workflows:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/workflow.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# Include modular makefiles
include makefiles/docker.mk
include makefiles/quality.mk
include makefiles/test.mk
include makefiles/database.mk
include makefiles/utils.mk
include makefiles/workflow.mk
