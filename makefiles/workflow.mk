# =============================================================================
# Development Workflows
# =============================================================================

# -----------------------------------------------------------------------------
# Quick Start (for new developers)
# -----------------------------------------------------------------------------
.PHONY: quick-start
quick-start: ## First-time setup for new developers
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "$(BOLD)  Quick Start - Setting up development environment$(RESET)"
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo -e "$(YELLOW)Step 1/5:$(RESET) Checking Docker..."
	$(call check_docker)
	@echo -e "$(GREEN)✓ Docker is running$(RESET)"
	@echo ""
	@echo -e "$(YELLOW)Step 2/5:$(RESET) Building Docker images..."
	@$(MAKE) build
	@echo ""
	@echo -e "$(YELLOW)Step 3/5:$(RESET) Starting services..."
	@$(MAKE) up
	@echo ""
	@echo -e "$(YELLOW)Step 4/5:$(RESET) Waiting for services to be healthy..."
	@sleep 10
	@echo ""
	@echo -e "$(YELLOW)Step 5/5:$(RESET) Running database migrations..."
	@$(MAKE) migrate-up || echo -e "$(YELLOW)No migrations to run$(RESET)"
	@echo ""
	@echo -e "$(BOLD)$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "$(BOLD)$(GREEN)  Setup complete! Your development environment is ready.$(RESET)"
	@echo -e "$(BOLD)$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo -e "  $(CYAN)API:$(RESET)         http://localhost:8080"
	@echo -e "  $(CYAN)Swagger:$(RESET)     http://localhost:8080/docs"
	@echo -e "  $(CYAN)Health:$(RESET)      http://localhost:8080/health-check"
	@echo ""
	@echo -e "  $(YELLOW)Useful commands:$(RESET)"
	@echo -e "    make logs      - View application logs"
	@echo -e "    make test      - Run tests"
	@echo -e "    make shell     - Access container shell"
	@echo -e "    make help      - Show all commands"
	@echo ""

# -----------------------------------------------------------------------------
# Development Workflows
# -----------------------------------------------------------------------------
.PHONY: dev
dev: build up logs ## Full development setup (build, up, logs)

.PHONY: dev-fresh
dev-fresh: down clean-cache build up logs ## Fresh development start (clean + rebuild)

.PHONY: dev-reset
dev-reset: ## Reset development environment (keeps data)
	@echo -e "$(YELLOW)Resetting development environment...$(RESET)"
	@$(MAKE) down
	@$(MAKE) clean-cache
	@$(MAKE) up
	@echo -e "$(GREEN)Development environment reset!$(RESET)"

.PHONY: dev-nuke
dev-nuke: ## Nuclear reset (WARNING: deletes everything)
	$(call confirm,WARNING: This will delete ALL data and rebuild from scratch!)
	@echo -e "$(RED)Nuclear reset in progress...$(RESET)"
	@$(MAKE) clean-all
	@$(MAKE) quick-start

# -----------------------------------------------------------------------------
# CI/CD Workflows
# -----------------------------------------------------------------------------
.PHONY: ci
ci: ## Run full CI pipeline
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo -e "$(BOLD)  Running CI Pipeline$(RESET)"
	@echo -e "$(BOLD)$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@$(MAKE) build
	@$(MAKE) up
	@sleep 5
	@$(MAKE) check
	@$(MAKE) test-cov
	@echo -e "$(GREEN)CI pipeline completed successfully!$(RESET)"

.PHONY: ci-quick
ci-quick: ## Quick CI check (format + lint + test)
	@echo -e "$(CYAN)Running quick CI check...$(RESET)"
	@$(MAKE) check
	@$(MAKE) test
	@echo -e "$(GREEN)Quick CI check passed!$(RESET)"

# -----------------------------------------------------------------------------
# Verification & Quality
# -----------------------------------------------------------------------------
.PHONY: verify
verify: ## Verify environment is working (status + checks + tests)
	@echo -e "$(CYAN)Verifying development environment...$(RESET)"
	@echo ""
	@echo -e "$(YELLOW)Services status:$(RESET)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo -e "$(YELLOW)Running code quality checks...$(RESET)"
	@$(MAKE) check
	@echo ""
	@echo -e "$(YELLOW)Running tests...$(RESET)"
	@$(MAKE) test
	@echo ""
	@echo -e "$(GREEN)Verification completed successfully!$(RESET)"

.PHONY: pre-push
pre-push: fix check test ## Run before pushing (format, lint, typecheck, test)
	@echo -e "$(GREEN)Pre-push checks passed! Safe to push.$(RESET)"

# -----------------------------------------------------------------------------
# Test Database Workflows
# -----------------------------------------------------------------------------
.PHONY: setup-test-db
setup-test-db: ## Setup test databases for E2E tests
	@echo -e "$(CYAN)Setting up test databases...$(RESET)"
	@$(MAKE) db-up
	@sleep 5
	@$(MAKE) test-db-create
	@echo -e "$(GREEN)Test databases ready!$(RESET)"

.PHONY: test-full
test-full: setup-test-db test-all ## Run all tests with test database setup
	@echo -e "$(GREEN)Full test suite completed!$(RESET)"

# -----------------------------------------------------------------------------
# Production Workflows
# -----------------------------------------------------------------------------
.PHONY: prod-deploy
prod-deploy: ## Deploy to production (build + up)
	@echo -e "$(CYAN)Deploying to production...$(RESET)"
	@$(MAKE) prod-build
	@$(MAKE) prod-up
	@echo -e "$(GREEN)Production deployment complete!$(RESET)"

.PHONY: prod-verify
prod-verify: ## Verify production environment
	@echo -e "$(CYAN)Verifying production environment...$(RESET)"
	@$(MAKE) prod-status
	@echo ""
	@curl -sf http://localhost:8080/health-check && echo -e "$(GREEN)Production health check passed!$(RESET)" || echo -e "$(RED)Production health check failed!$(RESET)"
