# Development Guide

## Docker-First Development Workflow

This project uses a **Docker-first development approach**. All development tasks are performed inside Docker containers using the provided Makefile.

## Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile)
- Git

## Getting Started

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd backend-fastapi-app

# Copy environment file (optional)
cp .env.example .env  # Edit as needed
```

### 2. Initial Setup

```bash
# Build and start everything
make dev
```

This single command will:
- Build all Docker images
- Start all services (Python app + PostgreSQL + MongoDB)
- Show application logs

### 3. Verify Setup

```bash
# Check service status
make status

# Check application health
make health

# Access API documentation
# Open http://localhost:8080/docs in browser
```

## Development Commands Reference

### Environment Management

```bash
# Build Docker images
make build

# Start/Stop services
make start            # Start all services (alias for up)
make stop             # Stop all services (alias for down)
make up               # Start all services in background
make down             # Stop all services

# Start with logs (foreground)
make up-logs

# Restart services
make restart

# Rebuild and restart (after code changes)
make rebuild

# Check service status
make status
```

### Development Workflow

```bash
# Full development setup (recommended)
make dev              # Build, start, and show logs

# Reset development environment
make dev-reset        # Clean restart

# Quick verification
make verify           # Check services, run tests and quality checks
```

### Code Quality

```bash
# Format code with ruff
make format

# Check code formatting
make format-check

# Run linting
make lint

# Run type checking with pyright
make typecheck

# Run all code quality checks
make check

# Format and fix all issues
make fix
```

### Testing

```bash
# Run unit tests
make test

# Run tests with coverage report
make test-cov

# Run integration tests (uses testcontainers)
make test-integration

# Run E2E tests (uses test databases)
make test-e2e

# Run all tests
make test-all

# Full CI pipeline
make ci               # Build, test, and check quality
```

### Database Management

```bash
# General Database Commands
make db-up            # Start both PostgreSQL and MongoDB
make db-down          # Stop both databases
make db-reset         # Reset all database data (WARNING: deletes all data)

# MongoDB Commands
make mongo-up         # Start only MongoDB
make mongo-down       # Stop MongoDB
make mongo-reset      # Reset MongoDB data
make shell-mongo      # Access MongoDB shell
make ping-mongo       # Ping MongoDB

# PostgreSQL Commands
make postgres-up      # Start only PostgreSQL
make postgres-down    # Stop PostgreSQL
make postgres-reset   # Reset PostgreSQL data
make shell-postgres   # Access PostgreSQL shell
make ping-postgres    # Ping PostgreSQL

# PostgreSQL Migrations (Alembic)
make migrate-generate MESSAGE="description"  # Generate new migration
make migrate-up       # Apply all pending migrations
make migrate-down     # Rollback one migration
make migrate-history  # Show migration history
make migrate-current  # Show current migration version
make migrate-reset    # Reset all migrations (WARNING: destroys data)

# PostgreSQL Seeding
make seed             # Seed database with sample data
make seed-clear       # Clear all seeded data
make reseed           # Clear and reseed with fresh data

# Test Database Management
make setup-test-db    # Setup test databases
make test-db-create   # Create test databases
make test-db-reset    # Reset test databases
```

### Container Access

```bash
# Access Python container shell
make shell

# Access Python REPL
make shell-python

# Access database shells
make shell-mongo      # MongoDB shell
make shell-postgres   # PostgreSQL shell
```

### Logging and Monitoring

```bash
# Show application logs
make logs

# Show database logs
make logs-db          # MongoDB logs
make logs-postgres    # PostgreSQL logs

# Show all services logs
make logs-all

# Check services status
make status
```

### Utilities

```bash
# Check application health
make health

# Show application version
make version

# Show API documentation URLs
make docs
```

### Production Commands

```bash
# Build production images
make prod-build

# Start production services
make prod-up

# Stop production services
make prod-down

# Show production logs
make prod-logs
```

### Cleanup

```bash
# Clean containers and images
make clean

# Deep clean (WARNING: removes all Docker data)
make clean-all

# Clean Python cache files
make clean-cache
```

## Development Best Practices

### 1. Never Run Commands Locally

**DO NOT** run these commands locally:
- `poetry install`
- `uvicorn` or `python` commands
- `pytest` or `ruff` commands
- `pip install` or any Python package management

**ALWAYS** use the Makefile commands that run everything inside Docker containers.

### 2. Code Quality Workflow

Before committing code:

```bash
# Fix formatting and linting issues
make fix

# Run all tests
make test

# Run full CI pipeline
make ci
```

### 3. Development Cycle

```bash
# 1. Start development environment
make dev

# 2. Make code changes in your editor
# Files are automatically synced to containers

# 3. Run tests for your changes
make test

# 4. Check code quality
make check

# 5. Fix any issues
make fix

# 6. Commit your changes
git add .
git commit -m "feat: your feature description"
```

### 4. Database Development

```bash
# Start fresh database
make db-reset

# Check database connection
make ping-db

# Access database shell for manual queries
make shell-mongo      # MongoDB
make shell-postgres   # PostgreSQL
```

## Container Architecture

### Services

- **python**: FastAPI application container
- **mongodb**: MongoDB database container (Log entity)
- **postgresql**: PostgreSQL database container (User entity)

### Volumes

- **Source code**: Mounted for hot reload during development
- **MongoDB data**: Persistent storage for MongoDB
- **PostgreSQL data**: Persistent storage for PostgreSQL

### Networks

- **Internal network**: Containers communicate via Docker network
- **External ports**:
  - Application: `localhost:8080`
  - PostgreSQL: `localhost:5432`
  - MongoDB: `localhost:27017`

## Development Environment Configuration

### Docker Compose Files

- `docker-compose.yaml`: Base configuration
- `docker-compose.override.yaml`: Development overrides
- `docker-compose.production.yaml`: Production environment

### Environment Variables

Create `.env` file in project root:

```env
# Application Settings
APP_NAME=backend-fastapi-app
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# PostgreSQL Settings
POSTGRE_DATABASE_URL=postgresql+asyncpg://admin:password@postgresql:5432/database_develop

# MongoDB Settings
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=backend_fastapi_app_dev
MONGODB_TEST_DB_NAME=backend_fastapi_app_test

# Server Settings
HOST=0.0.0.0
PORT=8080
RELOAD=true
```

### Hot Reload

The development environment supports hot reload:
- Code changes are automatically detected
- Application restarts automatically
- No need to rebuild containers for code changes

## Project Structure

```
app/
├── core/                    # Inner layers (no framework dependencies)
│   ├── domain/              # Domain layer (DDD patterns)
│   │   ├── aggregates/      # Aggregate roots
│   │   ├── entities/        # Domain entities
│   │   ├── value_objects/   # Value objects
│   │   ├── events/          # Domain events
│   │   ├── services/        # Domain services
│   │   ├── repositories/    # Repository interfaces
│   │   └── exceptions/      # Domain exceptions
│   └── application/         # Application layer (CQRS)
│       ├── commands/        # Write operations
│       ├── queries/         # Read operations
│       └── read_models/     # Read models
│
├── presentation/            # Presentation layer
│   ├── api/                 # REST API controllers
│   ├── dependencies/        # FastAPI DI
│   └── dtos/                # DTOs
│
├── infrastructure/          # Infrastructure layer
│   ├── configs/             # Configuration
│   ├── persistence/         # Database implementations
│   │   ├── postgresql/      # PostgreSQL (User)
│   │   └── mongodb/         # MongoDB (Log)
│   ├── messaging/           # Event bus
│   ├── event_handlers/      # Event handlers
│   └── web/                 # Middleware, exception handlers
│
└── main.py                  # Application entry point

tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── e2e/                     # E2E tests
└── conftest.py              # Shared fixtures
```

## Debugging

### Application Debugging

```bash
# View application logs
make logs

# Access container for debugging
make shell

# Check application health
make health
```

### Database Debugging

```bash
# View MongoDB logs
make logs-db

# Access MongoDB shell
make shell-mongo

# Access PostgreSQL shell
make shell-postgres

# Check database connections
make ping-mongo
make ping-postgres
```

### Common Issues

#### Container Won't Start

```bash
# Check container status
make status

# Check logs for errors
make logs-all

# Rebuild containers
make rebuild
```

#### Database Connection Issues

```bash
# Check databases are running
make ping-mongo
make ping-postgres

# Reset databases
make db-reset

# Check database logs
make logs-db
make logs-postgres
```

#### Permission Issues

```bash
# Clean and rebuild
make clean
make build
```

## IDE Integration

### VS Code

Recommended extensions:
- Python
- Docker
- MongoDB for VS Code
- PostgreSQL

### PyCharm

- Configure Docker as remote Python interpreter
- Set up MongoDB and PostgreSQL connections

### Code Style

The project uses Ruff for formatting and linting:
- Configure your IDE to use Ruff
- Or rely on `make format` and `make lint`

## Adding New Features

### 1. Domain Layer First

Start with domain models:

```python
# app/core/domain/entities/my_entity.py
class MyEntity:
    def __init__(self, id: MyEntityId, name: str):
        self.id = id
        self.name = name
```

### 2. Create Value Objects

```python
# app/core/domain/value_objects/my_value.py
@dataclass(frozen=True)
class MyValue:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValidationError("my_value", self.value)
```

### 3. Define Repository Interface

```python
# app/core/domain/repositories/my_entity.py
class IMyEntityRepository(Protocol):
    async def save(self, entity: MyEntity) -> None: ...
    async def get_by_id(self, id: MyEntityId) -> MyEntity | None: ...
```

### 4. Create Commands/Queries

```python
# app/core/application/commands/my_entity/create.py
@dataclass(frozen=True)
class CreateMyEntityCommand:
    name: str

# app/core/application/commands/handlers/my_entity_handlers.py
class CreateMyEntityHandler:
    async def handle(self, command: CreateMyEntityCommand) -> str:
        ...
```

### 5. Implement Repository

```python
# app/infrastructure/persistence/postgresql/repositories/my_entity.py
class PostgresMyEntityRepository(IMyEntityRepository):
    async def save(self, entity: MyEntity) -> None:
        ...
```

### 6. Create API Endpoint

```python
# app/presentation/api/v1/my_entity.py
@router.post("/")
async def create_my_entity(
    request: MyEntityCreateRequest,
    handler: CreateMyEntityHandlerDep,
) -> JSONResponse:
    ...
```

## Troubleshooting

### Common Commands

```bash
# Full reset
make clean
make dev

# Check everything is working
make verify

# View all logs
make logs-all

# Check service status
make status
```

### Log Analysis

```bash
# Application logs
make logs

# Database logs
make logs-db
make logs-postgres

# Follow logs in real-time
make logs-all  # Uses -f flag automatically
```

### Resource Issues

```bash
# Check Docker resources
docker system df

# Clean unused Docker data
make clean

# Deep clean (use with caution)
make clean-all
```
