# Database Management

# General Database Commands
.PHONY: db-up
db-up: ## Start both MongoDB and PostgreSQL
	@echo -e "$(GREEN)Starting databases...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up -d mongodb postgresql

.PHONY: db-down
db-down: ## Stop both databases
	@echo -e "$(YELLOW)Stopping databases...$(RESET)"
	$(DOCKER_COMPOSE_DEV) stop mongodb postgresql

.PHONY: db-reset
db-reset: ## Reset all database data (WARNING: deletes all data)
	@echo -e "$(RED)Resetting all database data...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down mongodb postgresql
	docker volume rm backend-fastapi-app_mongodb_data || true
	docker volume rm hr-app-test_postgresql_volume || true
	$(DOCKER_COMPOSE_DEV) up -d mongodb postgresql

# MongoDB Commands
.PHONY: mongo-up
mongo-up: ## Start only MongoDB
	@echo -e "$(GREEN)Starting MongoDB...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up -d mongodb

.PHONY: mongo-down
mongo-down: ## Stop MongoDB
	@echo -e "$(YELLOW)Stopping MongoDB...$(RESET)"
	$(DOCKER_COMPOSE_DEV) stop mongodb

.PHONY: mongo-reset
mongo-reset: ## Reset MongoDB data (WARNING: deletes all data)
	@echo -e "$(RED)Resetting MongoDB data...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down mongodb
	docker volume rm backend-fastapi-app_mongodb_data || true
	$(DOCKER_COMPOSE_DEV) up -d mongodb

.PHONY: shell-mongo
shell-mongo: ## Access MongoDB shell
	@echo -e "$(GREEN)Accessing MongoDB shell...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec mongodb mongosh

.PHONY: logs-db
logs-db: ## Show MongoDB logs
	@echo -e "$(GREEN)Showing MongoDB logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) logs -f mongodb

.PHONY: ping-mongo
ping-mongo: ## Ping MongoDB
	@echo -e "$(GREEN)Pinging MongoDB...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec mongodb mongosh --eval "db.adminCommand('ping')"

# PostgreSQL Commands
.PHONY: postgres-up
postgres-up: ## Start only PostgreSQL
	@echo -e "$(GREEN)Starting PostgreSQL...$(RESET)"
	$(DOCKER_COMPOSE_DEV) up -d postgresql

.PHONY: postgres-down
postgres-down: ## Stop PostgreSQL
	@echo -e "$(YELLOW)Stopping PostgreSQL...$(RESET)"
	$(DOCKER_COMPOSE_DEV) stop postgresql

.PHONY: postgres-reset
postgres-reset: ## Reset PostgreSQL data (WARNING: deletes all data)
	@echo -e "$(RED)Resetting PostgreSQL data...$(RESET)"
	$(DOCKER_COMPOSE_DEV) down postgresql
	docker volume rm hr-app-test_postgresql_volume || true
	$(DOCKER_COMPOSE_DEV) up -d postgresql

.PHONY: shell-postgres
shell-postgres: ## Access PostgreSQL shell
	@echo -e "$(GREEN)Accessing PostgreSQL shell...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec postgresql psql -U admin -d database_develop

.PHONY: logs-postgres
logs-postgres: ## Show PostgreSQL logs
	@echo -e "$(GREEN)Showing PostgreSQL logs...$(RESET)"
	$(DOCKER_COMPOSE_DEV) logs -f postgresql

.PHONY: ping-postgres
ping-postgres: ## Ping PostgreSQL
	@echo -e "$(GREEN)Pinging PostgreSQL...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec postgresql pg_isready -U admin -d database_develop

.PHONY: ping-db
ping-db: ## Ping both databases
	@echo -e "$(GREEN)Pinging MongoDB...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec mongodb mongosh --eval "db.adminCommand('ping')"
	@echo -e "$(GREEN)Pinging PostgreSQL...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec postgresql pg_isready -U admin -d database_develop

# Database Migrations (PostgreSQL)
.PHONY: migrate-generate
migrate-generate: ## Generate new migration (usage: make migrate-generate MESSAGE="your message")
	@echo -e "$(GREEN)Generating new migration...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run alembic revision --autogenerate -m "$(MESSAGE)"

.PHONY: migrate-up
migrate-up: ## Apply all pending migrations
	@echo -e "$(GREEN)Applying migrations...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run alembic upgrade head

.PHONY: migrate-down
migrate-down: ## Rollback one migration
	@echo -e "$(YELLOW)Rolling back one migration...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run alembic downgrade -1

.PHONY: migrate-history
migrate-history: ## Show migration history
	@echo -e "$(BLUE)Migration history:$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run alembic history

.PHONY: migrate-current
migrate-current: ## Show current migration version
	@echo -e "$(BLUE)Current migration:$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run alembic current

.PHONY: migrate-reset
migrate-reset: ## Reset all migrations (WARNING: destroys all data)
	@echo -e "$(RED)Resetting all migrations...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python poetry run alembic downgrade base

# Database Seeding (PostgreSQL)
.PHONY: seed
seed: ## Seed database with sample data
	@echo -e "$(GREEN)Seeding database with sample data...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python python app/databases/sql/seeds/seed_runner.py seed

.PHONY: seed-clear
seed-clear: ## Clear all seeded data (WARNING: removes sample data)
	@echo -e "$(YELLOW)Clearing all seeded data...$(RESET)"
	$(DOCKER_COMPOSE_DEV) exec python python app/databases/sql/seeds/seed_runner.py clear

.PHONY: reseed
reseed: seed-clear seed ## Clear and reseed database with fresh sample data
