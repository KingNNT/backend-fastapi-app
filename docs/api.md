# API Documentation

## Overview

This FastAPI application provides a RESTful API following Clean Architecture with CQRS patterns. All endpoints use standardized response formats and proper HTTP status codes.

## Base URL

- **Development**: `http://localhost:8080`
- **API Documentation**: `http://localhost:8080/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8080/redoc` (ReDoc)

## API Versioning

The API uses URL-based versioning with centralized prefix management:

```
/v1/users/     # User endpoints
/v1/logs/      # Log endpoints (future)
/health-check  # System endpoints (no version)
/version       # System endpoints (no version)
```

## Response Format

### Success Response

All successful responses follow this format:

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response payload
    },
    "meta": {
        // Optional metadata (pagination, etc.)
    }
}
```

### Error Response

All error responses follow this format:

```json
{
    "success": false,
    "message": "Error description",
    "error_code": "MACHINE_READABLE_CODE",
    "data": null,
    "context": {
        // Error-specific context
    }
}
```

### Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `USER_NOT_FOUND` | 404 | User with specified ID/email/username not found |
| `USER_ALREADY_EXISTS` | 409 | User with email/username already exists |
| `INVALID_USER_STATE` | 400 | Invalid state transition attempted |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## System Endpoints

### Health Check

Check application health status.

```http
GET /health-check
```

**Response** `200 OK`:
```json
{
    "success": true,
    "message": "Application is healthy",
    "data": {
        "status": "healthy",
        "timestamp": "2025-01-01T00:00:00Z",
        "checks": {
            "postgresql": "healthy",
            "mongodb": "healthy"
        }
    }
}
```

### Version

Get application version information.

```http
GET /version
```

**Response** `200 OK`:
```json
{
    "success": true,
    "message": "Version information",
    "data": {
        "version": "1.0.0",
        "environment": "development",
        "build_date": "2025-01-01T00:00:00Z"
    }
}
```

## User API (v1)

### Create User

Create a new user.

```http
POST /v1/users/
Content-Type: application/json
```

**Request Body**:
```json
{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securePassword123",
    "full_name": "John Doe"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email address |
| `username` | string | Yes | Unique username (3-50 chars) |
| `password` | string | Yes | Password (min 8 chars) |
| `full_name` | string | No | User's full name |

**Response** `201 Created`:
```json
{
    "success": true,
    "message": "User created successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

**Error Responses**:

`409 Conflict` - Email or username already exists:
```json
{
    "success": false,
    "message": "User with email 'user@example.com' already exists",
    "error_code": "USER_ALREADY_EXISTS",
    "context": {
        "field": "email",
        "value": "user@example.com"
    }
}
```

`422 Unprocessable Entity` - Validation error:
```json
{
    "success": false,
    "message": "Invalid email format",
    "error_code": "VALIDATION_ERROR",
    "context": {
        "field": "email",
        "value": "invalid-email"
    }
}
```

### List Users

Get paginated list of users.

```http
GET /v1/users/?skip=0&limit=10&include_deleted=false
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip |
| `limit` | integer | 10 | Maximum records to return (max: 100) |
| `include_deleted` | boolean | false | Include soft-deleted users |

**Response** `200 OK`:
```json
{
    "success": true,
    "message": "Users retrieved successfully",
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "is_active": true,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
    ],
    "meta": {
        "skip": 0,
        "limit": 10,
        "count": 1,
        "total": 1
    }
}
```

### Get User by ID

Retrieve a specific user by ID.

```http
GET /v1/users/{id}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | User's unique identifier |

**Response** `200 OK`:
```json
{
    "success": true,
    "message": "User retrieved successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
}
```

**Error Response** `404 Not Found`:
```json
{
    "success": false,
    "message": "User not found",
    "error_code": "USER_NOT_FOUND",
    "context": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

### Get User by Email

Retrieve a user by email address.

```http
GET /v1/users/by-email/{email}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `email` | string | User's email address (URL encoded) |

**Response** `200 OK`: Same as Get User by ID

### Get User by Username

Retrieve a user by username.

```http
GET /v1/users/by-username/{username}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | string | User's username |

**Response** `200 OK`: Same as Get User by ID

### Update User

Update an existing user.

```http
PUT /v1/users/{id}
Content-Type: application/json
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | User's unique identifier |

**Request Body** (all fields optional):
```json
{
    "email": "newemail@example.com",
    "username": "newusername",
    "password": "newPassword123",
    "full_name": "New Name"
}
```

**Response** `200 OK`:
```json
{
    "success": true,
    "message": "User updated successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

**Error Responses**:

`404 Not Found` - User not found
`409 Conflict` - Email/username already in use by another user

### Delete User

Soft delete a user (sets `deleted_at` timestamp).

```http
DELETE /v1/users/{id}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | User's unique identifier |

**Response** `204 No Content`: Empty response body

**Error Response** `404 Not Found`:
```json
{
    "success": false,
    "message": "User not found",
    "error_code": "USER_NOT_FOUND",
    "context": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

## Request/Response DTOs

### Request DTOs

Located in `app/presentation/dtos/user.py`:

```python
class UserCreateRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str | None = None

class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8)
    full_name: str | None = None
```

### Response DTOs

```python
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserListResponse(BaseModel):
    data: list[UserResponse]
    skip: int
    limit: int
    count: int
    total: int
```

## CQRS Flow

### Write Operations (Commands)

```
HTTP POST/PUT/DELETE
    ↓
Controller receives request
    ↓
Create Command (CreateUserCommand, UpdateUserCommand, etc.)
    ↓
Command Handler processes command
    ↓
Domain Aggregate performs business logic
    ↓
Repository persists changes
    ↓
Domain Events published
    ↓
Return success response
```

### Read Operations (Queries)

```
HTTP GET
    ↓
Controller receives request
    ↓
Create Query (GetUserByIdQuery, ListUsersQuery, etc.)
    ↓
Query Handler processes query
    ↓
Read Model Repository fetches data
    ↓
Return UserReadModel/list
    ↓
Serialize to response
```

## Error Handling

### Domain Exceptions

Domain exceptions are automatically converted to HTTP responses:

| Exception | HTTP Status | Error Code |
|-----------|-------------|------------|
| `UserNotFound` | 404 | `USER_NOT_FOUND` |
| `UserAlreadyExists` | 409 | `USER_ALREADY_EXISTS` |
| `InvalidUserState` | 400 | `INVALID_USER_STATE` |
| `ValidationError` | 422 | `VALIDATION_ERROR` |

### Exception Handler Registration

```python
# app/infrastructure/web/exception_handlers.py
def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(request: Request, exc: UserNotFound):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code.value,
                "context": exc.context,
            },
        )
```

## Authentication (Future)

Authentication is planned for future implementation. Current endpoints are open.

Planned features:
- JWT token-based authentication
- OAuth2 support
- Role-based access control (RBAC)

## Rate Limiting (Future)

Rate limiting is planned for future implementation.

Planned limits:
- 100 requests per minute per IP (general)
- 10 requests per minute for write operations
- 1000 requests per minute for authenticated users

## API Client Examples

### cURL

```bash
# Create user
curl -X POST http://localhost:8080/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"johndoe","password":"securePassword123"}'

# Get user by ID
curl http://localhost:8080/v1/users/550e8400-e29b-41d4-a716-446655440000

# List users with pagination
curl "http://localhost:8080/v1/users/?skip=0&limit=10"

# Update user
curl -X PUT http://localhost:8080/v1/users/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Updated Name"}'

# Delete user
curl -X DELETE http://localhost:8080/v1/users/550e8400-e29b-41d4-a716-446655440000
```

### Python (httpx)

```python
import httpx

BASE_URL = "http://localhost:8080"

async def create_user():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/users/",
            json={
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securePassword123",
            }
        )
        return response.json()

async def get_user(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/users/{user_id}")
        return response.json()

async def list_users(skip: int = 0, limit: int = 10):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/v1/users/",
            params={"skip": skip, "limit": limit}
        )
        return response.json()
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:8080';

// Create user
async function createUser(userData) {
    const response = await fetch(`${BASE_URL}/v1/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
    });
    return response.json();
}

// Get user by ID
async function getUser(userId) {
    const response = await fetch(`${BASE_URL}/v1/users/${userId}`);
    return response.json();
}

// List users
async function listUsers(skip = 0, limit = 10) {
    const response = await fetch(`${BASE_URL}/v1/users/?skip=${skip}&limit=${limit}`);
    return response.json();
}
```

## OpenAPI Specification

The full OpenAPI specification is available at:
- JSON: `http://localhost:8080/openapi.json`
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Best Practices

### Request Validation

All requests are validated using Pydantic models:
- Email format validation
- Required field checks
- Length constraints
- Type validation

### Response Consistency

All responses follow the standardized format:
- `success`: Boolean indicating operation result
- `message`: Human-readable message
- `data`: Response payload or null
- `error_code`: Machine-readable error code (errors only)
- `context`: Additional error context (errors only)

### Idempotency

- `GET` requests are idempotent
- `PUT` requests are idempotent (same input = same result)
- `DELETE` requests are idempotent (deleting already deleted = 404)
- `POST` requests may not be idempotent (creates new resources)

### Soft Deletion

Records are never hard-deleted:
- `DELETE` sets `deleted_at` timestamp
- Deleted records excluded from queries by default
- Use `include_deleted=true` to include deleted records
