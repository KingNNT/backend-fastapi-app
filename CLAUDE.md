# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Workflow (Docker-First)

This project uses a **Docker-first development approach**. All commands run inside Docker containers using the provided Makefile.

### Quick Start
```bash
# Build and start all services
make dev

# Or step by step:
make build    # Build Docker images
make up       # Start services
make logs     # View logs
```

### Essential Commands
```bash
# Development
make dev           # Full development setup (build, up, logs)
make up            # Start services in background
make down          # Stop all services
make restart       # Restart services
make rebuild       # Rebuild and restart

# Code Quality (runs in Docker)
make format        # Format code with ruff
make lint          # Run linting
make fix          # Format and fix all issues
make check        # Run all quality checks

# Testing (runs in Docker)
make test         # Run unit tests
make test-cov     # Run tests with coverage
make test-all     # Run all tests
make ci           # Full CI pipeline

# Database Management
make db-up        # Start only MongoDB
make db-reset     # Reset MongoDB data (WARNING: deletes all data)
make shell-mongo  # Access MongoDB shell

# Utilities
make shell        # Access Python container shell
make health       # Check application health
make version      # Show application version
```

### Never Run Locally
- **DO NOT** run `poetry install` locally
- **DO NOT** run `uvicorn` or `python` commands locally
- **DO NOT** run `pytest` or `ruff` commands locally
- **Always** use `make` commands which run everything in Docker containers
- The only exception is `make` itself, which orchestrates Docker containers

### Docker Services
- `python`: FastAPI application container
- `mongodb`: MongoDB database container
- Both services defined in `docker-compose.development.yaml`

## Architecture Overview

### Clean Architecture Pattern
This FastAPI application follows clean architecture principles with clear separation of concerns:

- **Models** (`app/internal/models/`): MongoDB documents using Beanie ODM, inherit from BaseEntity
- **DTOs** (`app/internal/dtos/`): Data Transfer Objects for API contracts, separate from internal models
- **Services** (`app/internal/services/`): Business logic layer with async MongoDB operations
- **Repositories** (`app/internal/repositories/`): Data access layer with MongoDB operations
- **Routers** (`app/routers/`): API layer with version-based organization (`v1/`)

### Technology Stack
- **Framework**: FastAPI with async support
- **Database**: MongoDB with Motor (async driver) and Beanie (ODM)
- **Containerization**: Docker with docker-compose
- **Code Quality**: Ruff for formatting and linting
- **Testing**: pytest with pytest-asyncio
- **Configuration**: Pydantic Settings with environment variables

### Key Architectural Decisions

**Base Entity Pattern**: All models inherit from `BaseEntity` (Beanie Document) providing:
- UUID-based IDs with automatic generation
- Audit trail fields (created_by, updated_by, deleted_by)
- Soft deletion with `deleted_at` field and `soft_delete()` method
- Timezone-aware datetime using `datetime.now(timezone.utc)`
- MongoDB indexes for performance

**MongoDB Integration**:
- Beanie ODM for async MongoDB operations
- Motor driver for high-performance async database access
- Database lifespan management in FastAPI application
- Connection pooling and automatic reconnection

**Repository Pattern**:
- Separate data access layer for MongoDB operations
- Async repository methods for CRUD operations
- Business logic separated from data access

**Configuration Management**:
- Pydantic Settings with environment variable support
- MongoDB connection string configuration
- Singleton pattern using `@lru_cache()` decorators
- Environment-aware configuration (development/staging/production)
- Structured logging configuration for uvicorn

**API Versioning**:
- Version-based routing under `/v1/` prefix
- Separate router modules for different API versions
- Clean upgrade path for API evolution

**Docker-First Development**:
- All development commands run in Docker containers
- MongoDB service integrated with docker-compose
- Makefile provides consistent development workflow
- No local Python environment required

### Data Flow Pattern
1. **Request** → Router (validation, serialization)
2. **Router** → Service (business logic, audit tracking)
3. **Service** → Repository (data access layer)
4. **Repository** → MongoDB (via Beanie ODM)
5. **Response** ← DTO (clean API contracts)

### Environment Configuration
The application uses environment-based configuration with `.env` file support:
- Development: Auto-reload, debug mode
- Production: Optimized settings, security headers
- Configurable via environment variables or `.env` file

### Database Strategy
MongoDB with Beanie ODM:
- Async operations with Motor driver
- Document-based storage with flexible schema
- Repository pattern abstracts data access
- Models inherit from Beanie Document
- UUID-based IDs support distributed systems
- Soft deletion preserves audit trail
- Indexes for performance optimization
- Connection management with lifespan events

### Testing Structure
- Unit tests: `app/tests/unit/` (business logic with mocked dependencies)
- E2E tests: `app/tests/e2e/` (full integration tests)
- Service layer testing with mock repositories
- pytest-asyncio for async test support
- pytest configuration in pyproject.toml
- All tests run in Docker containers via Makefile

## Important Implementation Details

### DateTime Handling
Always use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()` for timezone-aware datetime objects.

### Audit Trail
All entities automatically track:
- Who created/updated/deleted the record (`created_by`, `updated_by`, `deleted_by`)
- When these actions occurred (`created_at`, `updated_at`, `deleted_at`)
- Soft deletion preserves data for audit purposes

### Error Handling & Response Format
**Clean Architecture Pattern**: Services raise domain exceptions (never HTTPException), API layer converts to HTTP responses using class-based exception handlers and standardized APIResponse utility.

**Domain Exception Flow**:
1. Service layer raises domain exceptions (`UserNotFound`, `ValidationError`, etc.)
2. Exception handlers automatically convert to standardized HTTP responses
3. All responses follow consistent format via `APIResponse` utility

**Standardized Response Format**:
All API responses use consistent structure via `APIResponse` utility:

**Success Response**:
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { /* actual response data */ },
    "meta": { /* optional pagination/metadata */ }
}
```

**Error Response**:
```json
{
    "success": false,
    "message": "Error description",
    "error_code": "MACHINE_READABLE_CODE",
    "data": null,
    "context": { /* error-specific context */ }
}
```

**APIResponse Methods**:
- `APIResponse.success_response()` - For successful operations
- `APIResponse.error_response()` - For manual error responses
- `APIResponse.from_domain_exception()` - Auto-converts domain exceptions

### API Response Patterns
- Create: 201 Created with success response format
- Read: 200 OK with success response format
- Update: 200 OK with success response format
- Delete: 204 No Content with success response format
- Errors: Appropriate HTTP status with error response format

### MongoDB Specific
- All models inherit from Beanie's `Document` class via `BaseEntity`
- Use async/await for all database operations
- Repository pattern isolates MongoDB operations
- Connection managed through FastAPI lifespan events

### Development Workflow
- **Always run commands through Makefile** (Docker-first approach)
- Use `make format` and `make lint` before committing
- Run `make test` to ensure all tests pass
- Use `make ci` for full CI pipeline simulation
- Access services via `make shell` or `make shell-mongo`

## API Endpoints

### System Endpoints
- `GET /health-check` - Application health status
- `GET /version` - Application version info

### User API (v1)
- `POST /v1/users/` - Create new user
- `GET /v1/users/` - List users (with pagination)
- `GET /v1/users/{id}` - Get user by ID
- `PUT /v1/users/{id}` - Update user
- `DELETE /v1/users/{id}` - Soft delete user
- `GET /v1/users/by-email/{email}` - Get user by email

### API Documentation
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Environment Variables

### Application Settings
- `APP_NAME`: Application name
- `APP_VERSION`: Application version
- `ENVIRONMENT`: Environment (development/staging/production)
- `DEBUG`: Debug mode flag
- `LOG_LEVEL`: Logging level

### MongoDB Settings
- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name
- `MONGODB_TEST_DB_NAME`: Test database name

### Server Settings
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8080)
- `RELOAD`: Auto-reload on changes (development only)

## File Structure
```
app/
├── api/              # HTTP/API layer
│   ├── exception_handlers.py  # Class-based exception handlers
│   ├── dependencies.py        # FastAPI dependency injection
│   ├── middleware.py          # HTTP middleware
│   └── response.py            # Standardized API response utility
├── configs/          # Configuration modules
│   ├── app.py        # Main app configuration
│   ├── database.py   # MongoDB configuration
│   ├── logging.py    # Logging configuration
│   └── version.py    # Version management
├── exceptions/       # Domain exceptions (organized by domain)
│   ├── base.py       # Base exception classes
│   ├── user.py       # User domain exceptions
│   ├── validation.py # Validation & business rule exceptions
│   └── infrastructure.py  # Infrastructure exceptions
├── internal/         # Domain/business logic layer
│   ├── dtos/         # Data Transfer Objects
│   ├── models/       # MongoDB models (Beanie)
│   ├── repositories/ # Data access layer
│   └── services/     # Business logic
├── routers/          # API route handlers
│   ├── system.py     # System endpoints
│   └── v1/           # Version 1 API
│       └── user.py   # User endpoints
├── tests/            # Test suite
│   └── unit/         # Unit tests
└── main.py           # Application entry point
```
