# =============================================================================
# Database Management
# =============================================================================

# -----------------------------------------------------------------------------
# Database Variables (from .env with defaults)
# -----------------------------------------------------------------------------
POSTGRES_USER ?= admin
POSTGRES_DB ?= database_develop
POSTGRES_TEST_DB ?= database_test
MONGODB_TEST_DATABASE ?= backend_fastapi_app_test

# -----------------------------------------------------------------------------
# General Database Commands
# -----------------------------------------------------------------------------
.PHONY: db-up
db-up: ## Start all databases (MongoDB + PostgreSQL + Redis)
	@echo -e "$(GREEN)Starting databases...$(RESET)"
	$(DOCKER_COMPOSE) up -d mongodb postgresql redis

.PHONY: db-down
db-down: ## Stop all databases
	@echo -e "$(YELLOW)Stopping databases...$(RESET)"
	$(DOCKER_COMPOSE) stop mongodb postgresql redis

.PHONY: db-restart
db-restart: ## Restart all databases
	@echo -e "$(YELLOW)Restarting databases...$(RESET)"
	$(DOCKER_COMPOSE) restart mongodb postgresql redis

.PHONY: db-status
db-status: ## Show database services status
	@echo -e "$(CYAN)Database services status:$(RESET)"
	@$(DOCKER_COMPOSE) ps mongodb postgresql redis

.PHONY: db-reset
db-reset: ## Reset all database data (WARNING: deletes all data)
	$(call confirm,WARNING: This will delete ALL database data!)
	@echo -e "$(RED)Resetting all database data...$(RESET)"
	$(DOCKER_COMPOSE) down -v mongodb postgresql redis
	docker volume rm $(VOLUME_PREFIX)_mongodb_data $(VOLUME_PREFIX)_postgresql_data $(VOLUME_PREFIX)_redis_data 2>/dev/null || true
	$(DOCKER_COMPOSE) up -d mongodb postgresql redis
	@echo -e "$(GREEN)Databases reset successfully!$(RESET)"

.PHONY: db-ping
db-ping: ## Health check all databases
	@echo -e "$(CYAN)Checking database health...$(RESET)"
	@echo -e "$(YELLOW)MongoDB:$(RESET)"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) mongodb mongosh --eval "db.adminCommand('ping')" --quiet || echo -e "$(RED)MongoDB: Not responding$(RESET)"
	@echo -e "$(YELLOW)PostgreSQL:$(RESET)"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) postgresql pg_isready -U $(POSTGRES_USER) -d $(POSTGRES_DB) || echo -e "$(RED)PostgreSQL: Not responding$(RESET)"
	@echo -e "$(YELLOW)Redis:$(RESET)"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) redis redis-cli ping || echo -e "$(RED)Redis: Not responding$(RESET)"

.PHONY: db-logs
db-logs: ## Show all database logs
	@echo -e "$(GREEN)Showing database logs...$(RESET)"
	$(DOCKER_COMPOSE) logs -f mongodb postgresql redis

# -----------------------------------------------------------------------------
# MongoDB Commands
# -----------------------------------------------------------------------------
.PHONY: mongo-up
mongo-up: ## Start MongoDB
	@echo -e "$(GREEN)Starting MongoDB...$(RESET)"
	$(DOCKER_COMPOSE) up -d mongodb

.PHONY: mongo-down
mongo-down: ## Stop MongoDB
	@echo -e "$(YELLOW)Stopping MongoDB...$(RESET)"
	$(DOCKER_COMPOSE) stop mongodb

.PHONY: mongo-reset
mongo-reset: ## Reset MongoDB data (WARNING: deletes data)
	$(call confirm,WARNING: This will delete MongoDB data!)
	@echo -e "$(RED)Resetting MongoDB data...$(RESET)"
	$(DOCKER_COMPOSE) down mongodb
	docker volume rm $(VOLUME_PREFIX)_mongodb_data 2>/dev/null || true
	$(DOCKER_COMPOSE) up -d mongodb

.PHONY: mongo-shell
mongo-shell: ## Access MongoDB shell
	@echo -e "$(GREEN)Accessing MongoDB shell...$(RESET)"
	$(DOCKER_COMPOSE) exec mongodb mongosh

.PHONY: mongo-logs
mongo-logs: ## Show MongoDB logs
	$(DOCKER_COMPOSE) logs -f mongodb

# -----------------------------------------------------------------------------
# PostgreSQL Commands
# -----------------------------------------------------------------------------
.PHONY: postgres-up
postgres-up: ## Start PostgreSQL
	@echo -e "$(GREEN)Starting PostgreSQL...$(RESET)"
	$(DOCKER_COMPOSE) up -d postgresql

.PHONY: postgres-down
postgres-down: ## Stop PostgreSQL
	@echo -e "$(YELLOW)Stopping PostgreSQL...$(RESET)"
	$(DOCKER_COMPOSE) stop postgresql

.PHONY: postgres-reset
postgres-reset: ## Reset PostgreSQL data (WARNING: deletes data)
	$(call confirm,WARNING: This will delete PostgreSQL data!)
	@echo -e "$(RED)Resetting PostgreSQL data...$(RESET)"
	$(DOCKER_COMPOSE) down postgresql
	docker volume rm $(VOLUME_PREFIX)_postgresql_data 2>/dev/null || true
	$(DOCKER_COMPOSE) up -d postgresql

.PHONY: postgres-shell
postgres-shell: ## Access PostgreSQL shell
	@echo -e "$(GREEN)Accessing PostgreSQL shell...$(RESET)"
	$(DOCKER_COMPOSE) exec postgresql psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

.PHONY: postgres-logs
postgres-logs: ## Show PostgreSQL logs
	$(DOCKER_COMPOSE) logs -f postgresql

# -----------------------------------------------------------------------------
# Redis Commands
# -----------------------------------------------------------------------------
.PHONY: redis-up
redis-up: ## Start Redis
	@echo -e "$(GREEN)Starting Redis...$(RESET)"
	$(DOCKER_COMPOSE) up -d redis

.PHONY: redis-down
redis-down: ## Stop Redis
	@echo -e "$(YELLOW)Stopping Redis...$(RESET)"
	$(DOCKER_COMPOSE) stop redis

.PHONY: redis-shell
redis-shell: ## Access Redis CLI
	@echo -e "$(GREEN)Accessing Redis CLI...$(RESET)"
	$(DOCKER_COMPOSE) exec redis redis-cli

.PHONY: redis-logs
redis-logs: ## Show Redis logs
	$(DOCKER_COMPOSE) logs -f redis

# -----------------------------------------------------------------------------
# Database Migrations (PostgreSQL - Alembic)
# -----------------------------------------------------------------------------
.PHONY: migrate-generate
migrate-generate: ## Generate new migration (usage: make migrate-generate MSG="description")
ifndef MSG
	@echo -e "$(RED)Error: MSG is required$(RESET)"
	@echo -e "Usage: make migrate-generate MSG=\"add user table\""
	@exit 1
endif
	@echo -e "$(GREEN)Generating new migration...$(RESET)"
	$(DOCKER_EXEC) poetry run alembic revision --autogenerate -m "$(MSG)"

.PHONY: migrate-up
migrate-up: ## Apply all pending migrations
	@echo -e "$(GREEN)Applying migrations...$(RESET)"
	$(DOCKER_EXEC) poetry run alembic upgrade head

.PHONY: migrate-down
migrate-down: ## Rollback one migration
	@echo -e "$(YELLOW)Rolling back one migration...$(RESET)"
	$(DOCKER_EXEC) poetry run alembic downgrade -1

.PHONY: migrate-history
migrate-history: ## Show migration history
	@echo -e "$(CYAN)Migration history:$(RESET)"
	$(DOCKER_EXEC) poetry run alembic history

.PHONY: migrate-current
migrate-current: ## Show current migration version
	@echo -e "$(CYAN)Current migration:$(RESET)"
	$(DOCKER_EXEC) poetry run alembic current

.PHONY: migrate-reset
migrate-reset: ## Reset all migrations (WARNING: destroys data)
	$(call confirm,WARNING: This will reset all migrations and may destroy data!)
	@echo -e "$(RED)Resetting all migrations...$(RESET)"
	$(DOCKER_EXEC) poetry run alembic downgrade base

# -----------------------------------------------------------------------------
# Database Seeding (PostgreSQL)
# -----------------------------------------------------------------------------
.PHONY: seed
seed: ## Seed database with sample data
	@echo -e "$(GREEN)Seeding database with sample data...$(RESET)"
	$(DOCKER_EXEC) python app/infrastructure/persistence/postgresql/seeds/seed_runner.py seed

.PHONY: seed-clear
seed-clear: ## Clear all seeded data
	@echo -e "$(YELLOW)Clearing all seeded data...$(RESET)"
	$(DOCKER_EXEC) python app/infrastructure/persistence/postgresql/seeds/seed_runner.py clear

.PHONY: reseed
reseed: seed-clear seed ## Clear and reseed database

# -----------------------------------------------------------------------------
# Test Database Commands
# -----------------------------------------------------------------------------
.PHONY: test-db-create
test-db-create: ## Create test databases
	@echo -e "$(GREEN)Creating test databases...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) postgresql psql -U $(POSTGRES_USER) -d postgres -c "CREATE DATABASE $(POSTGRES_TEST_DB);" 2>/dev/null || echo -e "$(YELLOW)PostgreSQL test database already exists$(RESET)"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) mongodb mongosh --eval "use $(MONGODB_TEST_DATABASE)" --quiet || true
	@echo -e "$(GREEN)Test databases ready!$(RESET)"

.PHONY: test-db-reset
test-db-reset: ## Reset test databases (WARNING: deletes test data)
	@echo -e "$(RED)Resetting test databases...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) postgresql psql -U $(POSTGRES_USER) -d postgres -c "DROP DATABASE IF EXISTS $(POSTGRES_TEST_DB);"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) postgresql psql -U $(POSTGRES_USER) -d postgres -c "CREATE DATABASE $(POSTGRES_TEST_DB);"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) mongodb mongosh --eval "db.getSiblingDB('$(MONGODB_TEST_DATABASE)').dropDatabase()" --quiet
	@echo -e "$(GREEN)Test databases reset!$(RESET)"

.PHONY: test-db-clean
test-db-clean: ## Clean test database data (keeps structure)
	@echo -e "$(YELLOW)Cleaning test database data...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) postgresql psql -U $(POSTGRES_USER) -d $(POSTGRES_TEST_DB) -c "TRUNCATE TABLE users CASCADE;" 2>/dev/null || true
	@$(DOCKER_COMPOSE) exec $(EXEC_FLAGS) mongodb mongosh $(MONGODB_TEST_DATABASE) --eval "db.getCollectionNames().forEach(function(c) { db[c].deleteMany({}) })" --quiet 2>/dev/null || true
	@echo -e "$(GREEN)Test databases cleaned!$(RESET)"

.PHONY: test-db-shell-postgres
test-db-shell-postgres: ## Access PostgreSQL test database shell
	@echo -e "$(GREEN)Accessing PostgreSQL test database...$(RESET)"
	$(DOCKER_COMPOSE) exec postgresql psql -U $(POSTGRES_USER) -d $(POSTGRES_TEST_DB)

.PHONY: test-db-shell-mongo
test-db-shell-mongo: ## Access MongoDB test database shell
	@echo -e "$(GREEN)Accessing MongoDB test database...$(RESET)"
	$(DOCKER_COMPOSE) exec mongodb mongosh $(MONGODB_TEST_DATABASE)
