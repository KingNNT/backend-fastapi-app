# Development Workflow

.PHONY: dev
dev: build up logs ## Full development setup (build, up, logs)

.PHONY: dev-reset
dev-reset: down clean-cache up ## Reset development environment

.PHONY: ci
ci: build up test-cov check ## Run CI pipeline (build, up, test with coverage, check)
	@echo -e "$(GREEN)CI pipeline completed successfully!$(RESET)"

.PHONY: verify
verify: ## Quick verification (ensure services are up, run checks and tests)
	@echo -e "$(GREEN)Verifying services...$(RESET)"
	@$(DOCKER_COMPOSE_DEV) ps
	@$(MAKE) check test
	@echo -e "$(GREEN)Verification completed successfully!$(RESET)"
