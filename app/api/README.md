# API Layer

This package contains all HTTP/API related components that handle the translation between the external HTTP world and the internal domain logic.

## Structure

```
app/api/
├── __init__.py            # Package initialization
├── exception_handlers.py  # HTTP exception handling
├── dependencies.py        # FastAPI dependency injection
├── middleware.py          # HTTP middleware
└── README.md             # This file
```

## Components

### Exception Handlers (`exception_handlers.py`)

Converts domain exceptions to appropriate HTTP responses with structured error format:

```python
# Domain exception in service layer
raise UserNotFound(user_id="123")

# Automatically becomes HTTP response
{
    "detail": "User with ID '123' not found",
    "error_code": "USER_NOT_FOUND_BY_ID",
    "context": {
        "user_id": "123",
        "email": null,
        "username": null
    }
}
```

**Key Features:**
- Automatic status code mapping
- Structured error responses with context
- Machine-readable error codes
- Consistent error format across all endpoints

### Dependencies (`dependencies.py`)

Centralized dependency injection functions for FastAPI:

```python
@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_user(user_id)
```

**Benefits:**
- Single source of truth for service instantiation
- Easy to mock for testing
- Consistent service configuration
- Future-ready for advanced DI patterns

### Middleware (`middleware.py`)

HTTP middleware for cross-cutting concerns:

```python
# Request logging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request, process, log response
        pass

# Security headers
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add security headers
        pass
```

## Responsibilities

### What Belongs in API Layer:

✅ **HTTP-specific logic**
- Request/response handling
- Status code mapping
- HTTP headers and middleware
- Authentication/authorization decorators
- Rate limiting
- CORS configuration

✅ **Integration concerns**
- Exception handling
- Dependency injection
- Request validation schemas
- Response serialization
- API versioning logic

### What DOESN'T Belong Here:

❌ **Business logic** (belongs in `internal/services/`)
❌ **Data access** (belongs in `internal/repositories/`)
❌ **Domain models** (belongs in `internal/models/`)
❌ **Domain exceptions** (belongs in `exceptions/`)

## Usage Patterns

### Exception Handling

The API layer automatically handles all domain exceptions:

```python
# Service layer - just raise domain exceptions
class UserService:
    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)  # Domain exception
        return UserResponse(**user.model_dump())

# Router layer - no exception handling needed
@router.get("/{user_id}")
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    return await service.get_user(user_id)  # Auto-converts to HTTP response
```

### Dependency Injection

Use centralized dependencies:

```python
# Good - use centralized dependency
from app.api.dependencies import get_user_service

@router.get("/")
async def list_users(service: UserService = Depends(get_user_service)):
    return await service.get_users()

# Bad - local dependency function
def get_user_service():  # Don't duplicate this
    return UserService()
```

### Middleware Integration

Add middleware in `main.py`:

```python
from app.api.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
```

## Error Response Format

All error responses follow this consistent structure:

```json
{
    "detail": "Human-readable error message",
    "error_code": "MACHINE_READABLE_CODE",
    "context": {
        "field1": "value1",
        "field2": "value2"
    }
}
```

### Status Code Mapping

- `UserNotFound` → 404 Not Found
- `UserAlreadyExists` → 400 Bad Request
- `ValidationError` → 422 Unprocessable Entity
- `BusinessRuleViolation` → 400 Bad Request
- `DomainException` (generic) → 500 Internal Server Error

## Clean Architecture Compliance

The API layer serves as the **Interface Adapters** layer in Clean Architecture:

```
┌─────────────────────────────────────────┐
│           Frameworks & Drivers          │
│              (FastAPI)                  │
├─────────────────────────────────────────┤
│           Interface Adapters            │  ← API Layer (this package)
│     (Controllers, Presenters, Gateways) │
├─────────────────────────────────────────┤
│            Application Business         │  ← internal/services/
│               Rules                     │
├─────────────────────────────────────────┤
│              Enterprise                 │  ← internal/models/
│            Business Rules               │    exceptions/
└─────────────────────────────────────────┘
```

**Key Principles:**
- **Dependency Inversion**: API layer depends on domain abstractions
- **Interface Segregation**: Clean interfaces between layers
- **Single Responsibility**: Each component has one clear purpose
- **Open/Closed**: Easy to extend without modifying existing code

## Testing

### Testing Exception Handlers

```python
from app.api.exception_handlers import user_not_found_handler
from app.exceptions import UserNotFound

async def test_user_not_found_handler():
    exc = UserNotFound(user_id="123")
    response = await user_not_found_handler(Mock(), exc)

    assert response.status_code == 404
    content = json.loads(response.body)
    assert content["error_code"] == "USER_NOT_FOUND_BY_ID"
```

### Testing Dependencies

```python
from app.api.dependencies import get_user_service

def test_get_user_service():
    service = get_user_service()
    assert isinstance(service, UserService)
```

## Future Enhancements

### Authentication & Authorization

```python
# app/api/auth.py
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract user from JWT token."""
    pass

def require_permission(permission: str):
    """Decorator for permission-based access control."""
    pass
```

### Rate Limiting

```python
# app/api/rate_limiting.py
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting based on IP or user."""
    pass
```

### API Versioning

```python
# app/api/versioning.py
def api_version(version: str):
    """Decorator for API version handling."""
    pass
```

This API layer provides a clean, organized approach to handling all HTTP concerns while maintaining strict separation from business logic.
