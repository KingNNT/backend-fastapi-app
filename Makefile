# =============================================================================
# Makefile for backend-fastapi-app (Docker-first)
# =============================================================================

# Default shell
SHELL := /bin/bash

# -----------------------------------------------------------------------------
# Project Configuration
# -----------------------------------------------------------------------------
PROJECT_NAME := backend-fastapi-app
PYTHON_SERVICE := python
VOLUME_PREFIX := $(PROJECT_NAME)

# -----------------------------------------------------------------------------
# Docker Compose Configuration
# -----------------------------------------------------------------------------
# Development: uses docker-compose.yaml + docker-compose.override.yaml (automatic)
# Production: uses docker-compose.yaml + docker-compose.production.yaml (explicit)
DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.yaml -f docker-compose.production.yaml

# CI/Non-TTY support: set CI=true to disable TTY allocation
# Usage: make test CI=true
ifdef CI
    EXEC_FLAGS := -T
else
    EXEC_FLAGS :=
endif

# Docker exec shorthand
DOCKER_EXEC := $(DOCKER_COMPOSE) exec $(EXEC_FLAGS) $(PYTHON_SERVICE)
DOCKER_EXEC_PROD := $(DOCKER_COMPOSE_PROD) exec $(EXEC_FLAGS) $(PYTHON_SERVICE)

# -----------------------------------------------------------------------------
# Colors for Output
# -----------------------------------------------------------------------------
BOLD := \033[1m
RESET := \033[0m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BLUE := \033[34m
CYAN := \033[36m

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
define confirm
	@echo -e "$(RED)$(1)$(RESET)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
endef

define check_docker
	@docker info > /dev/null 2>&1 || (echo -e "$(RED)Error: Docker is not running$(RESET)" && exit 1)
endef

# -----------------------------------------------------------------------------
# Default Target
# -----------------------------------------------------------------------------
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "$(BOLD)  FastAPI Backend Commands (Docker-first)$(RESET)"
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Docker & Environment:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/docker.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Code Quality:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/quality.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Testing:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/test.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Database Management:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/database.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Utilities & Tools:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/utils.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(YELLOW)Development Workflows:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefiles/workflow.mk | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "  $(BOLD)Tip:$(RESET) Use $(CYAN)make <command>$(RESET) to run a command"
	@echo -e "  $(BOLD)Tip:$(RESET) Use $(CYAN)make <command> CI=true$(RESET) for non-TTY environments"
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"

# -----------------------------------------------------------------------------
# Include Modular Makefiles
# -----------------------------------------------------------------------------
include makefiles/docker.mk
include makefiles/quality.mk
include makefiles/test.mk
include makefiles/database.mk
include makefiles/utils.mk
include makefiles/workflow.mk
