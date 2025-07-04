# API Documentation

## Overview

This FastAPI application provides a RESTful API with automatic OpenAPI documentation, following REST conventions and API versioning best practices. All responses use a standardized format for consistency across endpoints.

## API Endpoints

### Base URL

- **Development**: `http://localhost:8080`
- **Production**: `https://your-domain.com`

### API Documentation

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI JSON**: `http://localhost:8080/openapi.json`

## Response Format

All API responses follow a standardized format for consistency across endpoints.

### Success Response Structure

```json
{
  "success": true,
  "message": "Human-readable success message",
  "data": { /* actual response data or null */ },
  "meta": { /* optional metadata like pagination info */ }
}
```

### Error Response Structure

```json
{
  "success": false,
  "message": "Human-readable error message",
  "error_code": "MACHINE_READABLE_ERROR_CODE",
  "data": null,
  "context": { /* error-specific context information */ }
}
```

### Field Descriptions

- **`success`**: Boolean indicating if the operation was successful
- **`message`**: Human-readable message describing the result
- **`data`**: The actual response payload (null for errors)
- **`meta`**: Optional metadata (pagination info, counts, etc.)
- **`error_code`**: Machine-readable error identifier (errors only)
- **`context`**: Additional error context (errors only)

## System Endpoints

### Health Check

```http
GET /health-check
```

**Description**: Check application health status

**Response**:
```json
{
  "success": true,
  "message": "Health check completed",
  "data": {
    "alive": true
  },
  "meta": null
}
```

**Status Codes**:
- `200 OK`: Application is healthy
- `503 Service Unavailable`: Application is unhealthy

### Version Information

```http
GET /version
```

**Description**: Get application version information

**Response**:
```json
{
  "success": true,
  "message": "Version information retrieved",
  "data": {
    "version": "1.0.0",
    "name": "backend-fastapi-app",
    "environment": "development"
  },
  "meta": null
}
```

**Status Codes**:
- `200 OK`: Version information retrieved

## User API (Version 1)

All user endpoints are prefixed with `/v1/users`.

### Create User

```http
POST /v1/users/
```

**Description**: Create a new user

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "securepassword123",
  "is_active": true
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "meta": null
}
```

**Status Codes**:
- `201 Created`: User created successfully
- `400 Bad Request`: Invalid input or email/username already exists
- `422 Unprocessable Entity`: Validation error

### Get User by ID

```http
GET /v1/users/{user_id}
```

**Description**: Retrieve a specific user by ID

**Path Parameters**:
- `user_id` (UUID): User identifier

**Response** (200 OK):
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "meta": null
}
```

**Status Codes**:
- `200 OK`: User retrieved successfully
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Invalid UUID format

### List Users

```http
GET /v1/users/
```

**Description**: Retrieve a list of users with pagination

**Query Parameters**:
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user1@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "email": "user2@example.com",
      "username": "janedoe",
      "full_name": "Jane Doe",
      "is_active": false,
      "created_at": "2024-01-15T11:00:00Z",
      "updated_at": "2024-01-15T11:30:00Z"
    }
  ],
  "meta": {
    "skip": 0,
    "limit": 100,
    "count": 2
  }
}
```

**Status Codes**:
- `200 OK`: Users retrieved successfully
- `422 Unprocessable Entity`: Invalid query parameters

### Update User

```http
PUT /v1/users/{user_id}
```

**Description**: Update an existing user

**Path Parameters**:
- `user_id` (UUID): User identifier

**Request Body** (all fields optional):
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Full Name",
  "is_active": false
}
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Full Name",
  "is_active": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Status Codes**:
- `200 OK`: User updated successfully
- `400 Bad Request`: Email or username already exists
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Validation error

### Delete User

```http
DELETE /v1/users/{user_id}
```

**Description**: Soft delete a user (marks as deleted but preserves data)

**Path Parameters**:
- `user_id` (UUID): User identifier

**Response** (204 No Content):
```json
{
  "success": true,
  "message": "User deleted successfully",
  "data": null,
  "meta": null
}
```

**Status Codes**:
- `204 No Content`: User deleted successfully
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Invalid UUID format

### Get User by Email

```http
GET /v1/users/by-email/{email}
```

**Description**: Retrieve a user by email address

**Path Parameters**:
- `email` (string): User email address

**Response** (200 OK):
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "meta": null
}
```

**Status Codes**:
- `200 OK`: User retrieved successfully
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Invalid email format

## Data Models

### User Create (Request)

```json
{
  "email": "string (email format, required)",
  "username": "string (3-50 chars, required)",
  "full_name": "string (optional)",
  "password": "string (min 8 chars, required)",
  "is_active": "boolean (default: true)"
}
```

**Validation Rules**:
- `email`: Valid email format, unique
- `username`: 3-50 characters, unique, alphanumeric and underscore only
- `full_name`: Optional, max 100 characters
- `password`: Minimum 8 characters
- `is_active`: Boolean, defaults to true

### User Update (Request)

```json
{
  "email": "string (email format, optional)",
  "username": "string (3-50 chars, optional)",
  "full_name": "string (optional)",
  "is_active": "boolean (optional)"
}
```

**Validation Rules**:
- All fields are optional
- Same validation rules as create for provided fields
- Password updates not supported via this endpoint

### User Response

```json
{
  "id": "UUID",
  "email": "string",
  "username": "string",
  "full_name": "string|null",
  "is_active": "boolean",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

**Notes**:
- `password` is never returned in responses
- `deleted_at` and audit fields are not exposed in API responses
- All timestamps are in UTC and ISO 8601 format

## Error Responses

All error responses follow the standardized error format with appropriate HTTP status codes.

### Common Error Examples

#### 400 Bad Request - User Already Exists

```json
{
  "success": false,
  "message": "User with email 'user@example.com' already exists",
  "error_code": "USER_ALREADY_EXISTS_BY_EMAIL",
  "data": null,
  "context": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 404 Not Found - User Not Found

```json
{
  "success": false,
  "message": "User with ID '123e4567-e89b-12d3-a456-426614174000' not found",
  "error_code": "USER_NOT_FOUND_BY_ID",
  "data": null,
  "context": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": null,
    "username": null
  }
}
```

#### 422 Unprocessable Entity - Validation Error

```json
{
  "success": false,
  "message": "Invalid email format",
  "error_code": "VALIDATION_ERROR",
  "data": null,
  "context": {
    "field": "email",
    "value": "invalid-email"
  }
}
```

#### 500 Internal Server Error

```json
{
  "success": false,
  "message": "An unexpected error occurred",
  "error_code": "INTERNAL_SERVER_ERROR",
  "data": null,
  "context": null
}
```

### Error Code Reference

- **`USER_NOT_FOUND_BY_ID`**: User not found by ID
- **`USER_NOT_FOUND_BY_EMAIL`**: User not found by email
- **`USER_NOT_FOUND_BY_USERNAME`**: User not found by username
- **`USER_ALREADY_EXISTS_BY_EMAIL`**: Email already registered
- **`USER_ALREADY_EXISTS_BY_USERNAME`**: Username already taken
- **`VALIDATION_ERROR`**: Input validation failed
- **`BUSINESS_RULE_VIOLATION`**: Business rule violated
- **`INTERNAL_SERVER_ERROR`**: Unexpected server error

## API Versioning

### Version Strategy

- **Path-based versioning**: `/v1/`, `/v2/`, etc.
- **Backward compatibility**: Old versions remain functional
- **Deprecation policy**: Minimum 6 months notice before removal

### Version 1 (Current)

- **Base path**: `/v1/`
- **Status**: Active
- **Features**: User CRUD operations

### Future Versions

- **Version 2**: Planned for advanced user features
- **Version 3**: Authentication and authorization

## Rate Limiting

### Current Status

- **Rate limiting**: Not implemented
- **Planned**: 1000 requests per minute per IP

### Headers

Future implementation will include:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## Authentication

### Current Status

- **Authentication**: Not implemented
- **Authorization**: Not implemented

### Future Implementation

- **JWT tokens**: For stateless authentication
- **Role-based access**: Admin, user roles
- **API keys**: For service-to-service communication

## Request/Response Examples

### Create User Example

**Request**:
```bash
curl -X POST "http://localhost:8080/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "password": "securepassword123",
    "is_active": true
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "john.doe@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "meta": null
}
```

### List Users Example

**Request**:
```bash
curl -X GET "http://localhost:8080/v1/users/?skip=0&limit=10"
```

**Response**:
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "john.doe@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "skip": 0,
    "limit": 10,
    "count": 1
  }
}
```

### Update User Example

**Request**:
```bash
curl -X PUT "http://localhost:8080/v1/users/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "is_active": false
  }'
```

**Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "john.doe@example.com",
  "username": "johndoe",
  "full_name": "John Smith",
  "is_active": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8080/health-check

# Create user
curl -X POST http://localhost:8080/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Get user
curl http://localhost:8080/v1/users/USER_ID
```

### Using Python requests

```python
import requests

# Create user
response = requests.post(
    "http://localhost:8080/v1/users/",
    json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
)
user = response.json()

# Get user
response = requests.get(f"http://localhost:8080/v1/users/{user['id']}")
print(response.json())
```

### Using the Interactive Docs

1. Visit `http://localhost:8080/docs`
2. Expand an endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

## Performance Considerations

### Response Times

- **Target**: < 200ms for simple operations
- **Database queries**: Optimized with indexes
- **Async operations**: Non-blocking I/O

### Pagination

- **Default limit**: 100 items
- **Maximum limit**: 1000 items
- **Offset-based**: Using `skip` and `limit` parameters

### Caching

- **Future implementation**: Redis for response caching
- **ETags**: For conditional requests
- **Cache headers**: Appropriate cache control

## Security Considerations

### Input Validation

- **Pydantic models**: Automatic validation
- **SQL injection**: Not applicable (NoSQL)
- **XSS prevention**: JSON-only responses

### Data Protection

- **Password hashing**: Planned implementation
- **Sensitive data**: Excluded from responses
- **Audit trails**: All changes tracked

### CORS

- **Current**: Permissive for development
- **Production**: Restricted to specific origins

## Monitoring and Logging

### Request Logging

- **All requests**: Logged with timestamp
- **Error tracking**: Detailed error logs
- **Performance metrics**: Response times tracked

### Health Monitoring

- **Health endpoint**: `/health-check`
- **Database connectivity**: Included in health check
- **Metrics**: Available for monitoring tools
