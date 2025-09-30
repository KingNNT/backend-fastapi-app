# FastAPI Backend Application

A modern, production-ready FastAPI backend application with MongoDB integration, following clean architecture principles and Docker-first development approach.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile)

### Getting Started

```bash
# Clone and start the application
git clone <repository-url>
cd backend-fastapi-app
make dev
```

**That's it!** The application will be available at:
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health-check

## 🛠️ Technology Stack

- **Framework**: FastAPI with async support
- **Databases**:
  - **PostgreSQL** with SQLModel and Alembic for migrations (SQL)
  - **MongoDB** with Beanie ODM and Motor driver (NoSQL)
- **Language**: Python 3.12+
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with async support and comprehensive mocking
- **Code Quality**: Ruff (formatting & linting), Pyright (type checking)
- **Architecture**: Clean Architecture with dependency injection

## 🏗️ Architecture

This application follows clean architecture with clear separation of concerns and modern design patterns:

```
┌─────────────────────────────────────┐
│        API Layer (FastAPI)          │  ← Routers, middleware, dependencies
├─────────────────────────────────────┤
│     Business Logic (Services)       │  ← Singleton services with DI
├─────────────────────────────────────┤
│     Data Access (Repositories)      │  ← Repository pattern for data access
├─────────────────────────────────────┤
│     Databases (Dual Support)        │  ← PostgreSQL (SQLModel) + MongoDB (Beanie)
└─────────────────────────────────────┘
```

### Key Architectural Features

- **🔄 Singleton Pattern**: Services use singleton pattern with proper dependency injection
- **📦 Barrel Exports**: Clean imports using `__init__.py` files for better module organization
- **🏗️ Repository Pattern**: Separation of data access logic from business logic
- **📝 Global Logging**: Centralized logging configuration with datetime formatting
- **🔌 Middleware Organization**: Structured middleware in dedicated `dependencies/` folder
- **🚀 API Versioning**: Centralized v1 router architecture with prefix management

## 📁 Project Structure

```
app/
├── configs/         # Configuration modules (app, database, logging, version)
│   └── __init__.py  # Barrel exports for all configs
├── dependencies/    # Dependency injection and middleware
│   ├── middleware.py    # Request logging and security middleware
│   └── __init__.py      # Exports for dependency injection
├── internal/        # Domain/business logic layer
│   ├── dtos/            # Data Transfer Objects with barrel exports
│   ├── exceptions/      # Domain exceptions organized by type
│   ├── models/          # MongoDB models with BaseEntity
│   ├── repositories/    # Data access layer with repository pattern
│   ├── services/        # Business logic with singleton pattern
│   └── __init__.py      # Internal module exports
├── routers/         # API endpoints with version organization
│   ├── v1/              # Version 1 API with centralized routing
│   ├── system.py        # System endpoints (health, version)
│   └── __init__.py      # Router exports
├── utils/           # Utility functions and helpers
│   ├── response.py      # Standardized API response utilities
│   └── __init__.py      # Utility exports
├── tests/           # Comprehensive test suite
│   ├── unit/            # Unit tests with mocking
│   ├── e2e/             # End-to-end integration tests
│   └── conftest.py      # Shared test configuration
└── main.py          # Application entry point with global configs
```

## 🔧 Development

### Essential Commands

```bash
# Development workflow
make dev             # Start development environment
make test            # Run tests
make fix             # Format and lint code
make ci              # Run full CI pipeline

# Database management
make db-up           # Start both databases
make db-reset        # Reset all database data
make shell-mongo     # Access MongoDB shell
make shell-postgres  # Access PostgreSQL shell
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

Full API documentation available at http://localhost:8080/docs

## 📚 Detailed Documentation

For comprehensive guides, see the `docs/` directory:

- **[Architecture](docs/architecture.md)** - Detailed architecture, patterns, and design decisions
- **[Development](docs/development.md)** - Complete development workflow and Docker commands
- **[API Documentation](docs/api.md)** - Full API reference with examples
- **[Database](docs/database.md)** - MongoDB schema, queries, and optimization
- **[Testing](docs/testing.md)** - Testing strategies, patterns, and best practices
- **[Deployment](docs/deployment.md)** - Production deployment guides and monitoring

## 🧪 Features

### Core Features
- ✅ **Clean Architecture** with dependency injection and singleton services
- ✅ **Dual Database Support**:
  - PostgreSQL (SQLModel + Alembic migrations) for relational data
  - MongoDB (Beanie ODM + Motor) for document storage
- ✅ **Unified Lifespan Management** for both databases
- ✅ **API Versioning** with centralized `/v1/` prefix management
- ✅ **Comprehensive Testing** (unit tests with mocks and E2E tests)
- ✅ **Docker-First Development** (no local Python needed)
- ✅ **Modular Makefile** organized by functionality

### Advanced Features
- ✅ **Audit Trail** with soft deletion and automatic tracking
- ✅ **Global Logging** with datetime formatting and structured output
- ✅ **Barrel Exports** for clean module imports and organization
- ✅ **Middleware Architecture** with request logging and security headers
- ✅ **Exception Handling** with domain-specific exception hierarchy
- ✅ **Repository Pattern** for clean data access abstraction

### Quality & DevOps
- ✅ **Code Quality** with Ruff formatting/linting and Pyright type checking
- ✅ **Health Checks** and monitoring endpoints
- ✅ **Environment Configuration** with Pydantic Settings
- ✅ **Pre-commit Hooks** for automated code quality
- ✅ **Make-based Workflow** for consistent development experience

## 🔒 Security & Best Practices

- **Soft Deletion**: Records preserved for audit trail
- **Audit Trail**: All changes tracked automatically with timestamps and user tracking
- **Input Validation**: Pydantic models ensure data integrity and type safety
- **UUID-based IDs**: Prevents enumeration attacks and supports distributed systems
- **Environment Variables**: Secure configuration management with Pydantic Settings
- **Security Headers**: Automatic security headers via middleware
- **Request Logging**: Comprehensive request/response logging with timing

## 🚀 Production Ready

### Deployment Options
- **Docker Compose**: Single-server deployment for small to medium applications
- **Kubernetes**: Scalable production deployment for enterprise applications
- **Health Checks**: Application and database monitoring with `/health-check` endpoint

### Performance Features
- **Async Operations**: Full async/await support with connection pooling
- **Connection Pooling**: MongoDB connection pooling via Motor
- **Lazy Loading**: Efficient data loading patterns
- **Logging**: Structured logging with datetime formatting for production monitoring

### Monitoring & Observability
- **Health Endpoints**: `/health-check` and `/version` for monitoring
- **Request Logging**: Detailed request/response logging with timing
- **Error Tracking**: Comprehensive exception handling and logging
- **Performance Metrics**: Response time tracking via middleware

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and run tests: `make ci`
4. Submit a pull request

### Code Standards

- Follow clean architecture principles with proper separation of concerns
- Use singleton pattern for services with dependency injection
- Implement repository pattern for data access
- Write comprehensive tests with proper mocking
- Use barrel exports for clean module organization
- Follow the established logging patterns
- Use type hints and proper documentation
- Run `make fix` before committing

### Development Guidelines

- **Services**: Use singleton pattern with dependency injection
- **Imports**: Use barrel exports from `__init__.py` files
- **Logging**: Use `logging.getLogger(__name__)` for consistent logging
- **Testing**: Write unit tests with mocks and E2E tests for integration
- **API Design**: Follow RESTful principles with proper HTTP status codes
- **Error Handling**: Use domain exceptions, not HTTP exceptions in services

## 📄 License

This project is licensed under the MIT License.

## 🆘 Quick Help

```bash
make help           # Show all available commands
make dev            # Start development (most common)
make test           # Run tests
make ci             # Full CI pipeline
make health         # Check application health
make shell          # Access container shell
```

For detailed guides, check the [documentation](docs/) directory.

## 🔥 Recent Improvements

This template includes modern architectural improvements:

- **Singleton Services**: Efficient service layer with proper dependency injection
- **Barrel Exports**: Clean import structure with `__init__.py` organization
- **Global Logging**: Centralized logging configuration with datetime formatting
- **Middleware Organization**: Structured middleware in dedicated folder
- **API Versioning**: Centralized v1 router architecture
- **Exception Architecture**: Comprehensive domain exception hierarchy

---

**Ready to build something amazing! 🚀**
