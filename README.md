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
- **Database**: MongoDB with Beanie ODM
- **Language**: Python 3.12+
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with async support
- **Code Quality**: Ruff (formatting & linting)

## 🏗️ Architecture

This application follows clean architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│           API Layer (FastAPI)       │
├─────────────────────────────────────┤
│        Business Logic (Services)    │
├─────────────────────────────────────┤
│       Data Access (Repositories)    │
├─────────────────────────────────────┤
│        Database (MongoDB)           │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
app/
├── api/             # HTTP/API layer (exception handlers, dependencies, middleware)
├── configs/         # Configuration modules
├── exceptions/      # Domain exceptions (organized by domain)
├── internal/        # Domain/business logic layer
│   ├── dtos/       # Data Transfer Objects
│   ├── models/     # MongoDB models
│   ├── repositories/# Data access layer
│   └── services/   # Business logic
├── routers/        # API endpoints
├── tests/          # Test suite
└── main.py         # Application entry point
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
make db-reset        # Reset database
make shell-mongo     # Access MongoDB shell

# Utilities
make shell           # Access container shell
make health          # Check application health
```

> **Note**: All commands run in Docker containers. Never run Python commands locally.

### API Endpoints

- **System**: `/health-check`, `/version`
- **Users (v1)**: `/v1/users/` (CRUD operations)

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

- ✅ **Clean Architecture** with dependency injection
- ✅ **MongoDB Integration** with async ODM (Beanie)
- ✅ **API Versioning** (`/v1/` prefix)
- ✅ **Comprehensive Testing** (unit tests with mocks)
- ✅ **Docker-First Development** (no local Python needed)
- ✅ **Audit Trail** with soft deletion
- ✅ **Code Quality** with Ruff formatting/linting
- ✅ **Health Checks** and monitoring endpoints
- ✅ **Environment Configuration** with Pydantic Settings

## 🔒 Security & Best Practices

- **Soft Deletion**: Records preserved for audit
- **Audit Trail**: All changes tracked automatically
- **Input Validation**: Pydantic models ensure data integrity
- **UUID-based IDs**: Prevents enumeration attacks
- **Environment Variables**: Secure configuration management

## 🚀 Production Ready

- **Docker Compose**: Single-server deployment
- **Kubernetes**: Scalable production deployment
- **Health Checks**: Application and database monitoring
- **Logging**: Structured JSON logging
- **Performance**: Async operations with connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and run tests: `make ci`
4. Submit a pull request

### Code Standards

- Follow clean architecture principles
- Write comprehensive tests
- Use type hints and proper documentation
- Run `make fix` before committing

## 📄 License

This project is licensed under the MIT License.

## 🆘 Quick Help

```bash
make help           # Show all available commands
make dev            # Start development (most common)
make test           # Run tests
make ci             # Full CI pipeline
```

For detailed guides, check the [documentation](docs/) directory.

---

**Ready to build something amazing! 🚀**
