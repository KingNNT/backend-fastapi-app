# FastAPI Backend Application

A modern, production-ready FastAPI backend application following Clean Architecture with Domain-Driven Design (DDD) and CQRS patterns. Features dual database support (PostgreSQL + MongoDB) and a Docker-first development approach.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile)

### Getting Started

Create a new project from this template with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/KingNNT/backend-fastapi-app/develop/install.sh | bash
```

The installer will prompt you for:
- **Project name** (kebab-case, e.g., `my-awesome-api`)
- **Project description**
- **Author name and email**

Then it automatically clones the template, updates all configuration files, and initializes a fresh git repository.

After installation:
```bash
cd your-project-name
make dev
```

**That's it!** The application will be available at:
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health-check

## Technology Stack

- **Framework**: FastAPI with async support
- **Databases**:
  - **PostgreSQL** with SQLModel and Alembic for migrations
  - **MongoDB** with Beanie ODM and Motor driver
- **Language**: Python 3.12+
- **Architecture**: Clean Architecture + DDD + CQRS
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with async support, testcontainers
- **Code Quality**: Ruff (formatting & linting), Pyright (type checking)

## Architecture

This application follows Clean Architecture with Domain-Driven Design tactical patterns and full CQRS:

```
┌─────────────────────────────────────────────────────┐
│              Presentation Layer                      │
│     (FastAPI Controllers, DTOs, Dependencies)        │
├─────────────────────────────────────────────────────┤
│              Application Layer                       │
│   (Commands, Queries, Handlers, Read Models)         │
├─────────────────────────────────────────────────────┤
│                Domain Layer                          │
│ (Aggregates, Entities, Value Objects, Domain Events) │
├─────────────────────────────────────────────────────┤
│             Infrastructure Layer                     │
│   (Repositories, Event Bus, Database Connections)    │
└─────────────────────────────────────────────────────┘
```

### Key Architectural Features

- **Domain-Driven Design**: Aggregates, Entities, Value Objects, Domain Events
- **CQRS Pattern**: Separate command (write) and query (read) paths
- **Unit of Work**: Transaction coordination with auto-commit/rollback and event publishing
- **Domain Services**: Stateless validation services for cross-entity business rules
- **Event-Driven**: Domain events trigger side effects (audit logs, notifications)
- **Repository Pattern**: Abstract data access with Protocol-based interfaces
- **Dependency Injection**: FastAPI Depends with setter functions for runtime config
- **RBAC System**: Role-based access control with users, roles, and permissions

## Project Structure

```
app/
├── core/                    # Inner layers (no framework dependencies)
│   ├── domain/              # Layer 1: Domain (DDD patterns)
│   │   ├── aggregates/      # Aggregate roots (UserAggregate, LogAggregate)
│   │   ├── entities/        # Entities (User, Log)
│   │   ├── value_objects/   # Value objects (Email, Username, UserId)
│   │   ├── events/          # Domain events (UserCreated, UserUpdated, etc.)
│   │   ├── specifications/  # Business rules
│   │   ├── services/        # Domain services
│   │   ├── repositories/    # Repository interfaces (Protocols)
│   │   └── exceptions/      # Domain exceptions
│   │
│   └── application/         # Layer 2: Application (CQRS)
│       ├── commands/        # Write side (CreateUser, UpdateUser, etc.)
│       ├── queries/         # Read side (GetUser, ListUsers, etc.)
│       ├── read_models/     # Optimized read models
│       └── interfaces/      # Application interfaces
│
├── presentation/            # Layer 3: Presentation
│   ├── api/                 # REST API controllers
│   │   ├── v1/              # API version 1
│   │   └── system.py        # Health & version endpoints
│   ├── dependencies/        # FastAPI dependency injection
│   └── dtos/                # Data Transfer Objects
│
├── infrastructure/          # Layer 4: Infrastructure
│   ├── configs/             # Configuration (app, logging, version)
│   ├── persistence/         # Database implementations
│   │   ├── postgresql/      # PostgreSQL (User entity)
│   │   └── mongodb/         # MongoDB (Log entity)
│   ├── messaging/           # Event bus, password hasher
│   ├── event_handlers/      # Domain event handlers
│   ├── web/                 # Middleware, exception handlers
│   └── setup.py             # Dependency injection setup
│
└── main.py                  # Application entry point

tests/                       # Test suite (outside app/)
├── unit/                    # Unit tests
├── integration/             # Integration tests (testcontainers)
├── e2e/                     # End-to-end tests
└── conftest.py              # Shared fixtures
```

## Development

### Essential Commands

```bash
# Development workflow
make dev             # Start development environment
make test            # Run unit tests
make test-e2e        # Run E2E tests
make fix             # Format and lint code
make ci              # Run full CI pipeline

# Database management
make db-up           # Start both databases
make db-reset        # Reset all database data
make migrate-up      # Apply PostgreSQL migrations
make seed            # Seed PostgreSQL with sample data

# Utilities
make shell           # Access container shell
make health          # Check application health
```

> **Note**: All commands run in Docker containers. Never run Python commands locally.

### API Endpoints

#### System Endpoints
- `GET /health-check` - Application health status
- `GET /version` - Application version info

#### User API (v1)
- `POST /v1/users/` - Create new user
- `GET /v1/users/` - List users (with pagination)
- `GET /v1/users/{id}` - Get user by ID
- `PUT /v1/users/{id}` - Update user
- `DELETE /v1/users/{id}` - Soft delete user
- `GET /v1/users/by-email/{email}` - Get user by email
- `GET /v1/users/by-username/{username}` - Get user by username
- `GET /v1/users/{id}/roles` - Get user's assigned roles
- `POST /v1/users/{id}/roles` - Assign role to user
- `DELETE /v1/users/{id}/roles/{role_id}` - Remove role from user
- `GET /v1/users/{id}/permissions` - Get user's effective permissions
- `POST /v1/users/{id}/permissions` - Assign permission to user
- `DELETE /v1/users/{id}/permissions/{permission_id}` - Remove permission from user

#### Role API (v1)
- `POST /v1/roles/` - Create new role
- `GET /v1/roles/` - List roles
- `GET /v1/roles/{id}` - Get role by ID
- `PUT /v1/roles/{id}` - Update role
- `DELETE /v1/roles/{id}` - Delete role
- `GET /v1/roles/{id}/permissions` - Get role's permissions
- `POST /v1/roles/{id}/permissions` - Assign permission to role
- `DELETE /v1/roles/{id}/permissions/{permission_id}` - Remove permission from role

#### Permission API (v1)
- `POST /v1/permissions/` - Create new permission
- `GET /v1/permissions/` - List permissions
- `GET /v1/permissions/{id}` - Get permission by ID
- `PUT /v1/permissions/{id}` - Update permission
- `DELETE /v1/permissions/{id}` - Delete permission

Full API documentation available at http://localhost:8080/docs

## Documentation

For comprehensive guides, see the `docs/` directory:

- **[Architecture](docs/architecture.md)** - Clean Architecture, DDD, and CQRS patterns
- **[Development](docs/development.md)** - Development workflow and Docker commands
- **[API Documentation](docs/api.md)** - Full API reference with examples
- **[Database](docs/database.md)** - Dual database strategy (PostgreSQL + MongoDB)
- **[Testing](docs/testing.md)** - Testing strategies and patterns
- **[Deployment](docs/deployment.md)** - Production deployment guides

## Features

### Core Features
- Clean Architecture with clear layer separation
- Domain-Driven Design tactical patterns
- CQRS (Command Query Responsibility Segregation)
- Unit of Work pattern for transaction management
- Domain Services for validation logic
- RBAC (Role-Based Access Control) system
- Dual Database Support (PostgreSQL + MongoDB)
- Event-Driven Architecture with domain events
- API Versioning with centralized prefix management
- Comprehensive Testing (unit, integration, E2E)
- Docker-First Development

### Advanced Features
- Audit Trail with soft deletion
- Global Logging with datetime formatting
- Domain Exception Handling
- Standardized API Response Format
- Repository Pattern with Protocol interfaces
- Mapper Pattern for entity/model conversion

### Quality & DevOps
- Code Quality with Ruff and Pyright
- Health Checks and monitoring
- Environment Configuration with Pydantic Settings
- Make-based Workflow

## Security & Best Practices

- **Soft Deletion**: Records preserved for audit trail
- **Audit Trail**: All changes tracked with timestamps
- **Input Validation**: Pydantic models and Value Objects
- **UUID-based IDs**: Prevents enumeration attacks
- **Domain Exceptions**: Clean error handling without HTTP leakage
- **Security Headers**: Automatic headers via middleware

## Production Ready

### Deployment Options
- **Docker Compose**: Single-server deployment
- **Kubernetes**: Scalable production deployment
- **Health Checks**: Application and database monitoring

### Performance Features
- **Async Operations**: Full async/await support
- **Connection Pooling**: Both PostgreSQL and MongoDB
- **Optimized Read Models**: CQRS for read performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and run tests: `make ci`
4. Submit a pull request

### Code Standards

- Follow Clean Architecture principles
- Use DDD patterns (Aggregates, Value Objects, Domain Events)
- Implement CQRS for commands and queries
- Write comprehensive tests
- Use type hints and proper documentation
- Run `make fix` before committing

## License

This project is licensed under the MIT License.

## Quick Help

```bash
make help           # Show all available commands
make dev            # Start development (most common)
make test           # Run tests
make ci             # Full CI pipeline
```

For detailed guides, check the [documentation](docs/) directory.
