# Exceptions Module

This module provides a comprehensive exception hierarchy for the application, following domain-driven design principles and clean architecture patterns.

## Structure

```
app/exceptions/
├── __init__.py           # Public API exports
├── base.py              # Base exception classes
├── user.py              # User domain exceptions
├── validation.py        # Validation and business rule exceptions
├── infrastructure.py    # Infrastructure-related exceptions
├── examples.py          # Usage examples
└── README.md           # This file
```

## Exception Hierarchy

### Base Exceptions

- **`DomainException`**: Root exception for all domain errors
- **`ApplicationException`**: Application-level errors
- **`InfrastructureException`**: Infrastructure-related errors

### User Domain Exceptions

- **`UserException`**: Base for user-related errors
- **`UserNotFound`**: User doesn't exist (by ID, email, or username)
- **`UserAlreadyExists`**: Duplicate user creation attempts
- **`UserInactive`**: Operations on inactive users
- **`UserPermissionDenied`**: Permission violations
- **`UserAccountLocked`**: Account locked scenarios

### Validation Exceptions

- **`ValidationException`**: Base for validation errors
- **`ValidationError`**: Field validation failures
- **`BusinessRuleViolation`**: Business rule violations
- **`InvalidOperationError`**: Invalid operations in current context
- **`DataIntegrityError`**: Data integrity constraint violations
- **`ConcurrencyError`**: Concurrent modification conflicts

### Infrastructure Exceptions

- **`DatabaseException`**: Database-related errors
- **`ExternalServiceException`**: External service failures
- **`FileSystemException`**: File system errors

## Features

### Error Codes

All exceptions include machine-readable error codes:

```python
try:
    service.get_user(user_id)
except UserNotFound as e:
    print(e.error_code)  # "USER_NOT_FOUND_BY_ID"
    print(e.message)     # "User with ID '123' not found"
```

### Rich Context

Exceptions carry structured context information:

```python
try:
    service.create_user(user_data)
except UserAlreadyExists as e:
    print(e.field)  # "email"
    print(e.value)  # "user@example.com"
```

### HTTP Integration

Exceptions automatically translate to appropriate HTTP responses:

- `UserNotFound` → 404 Not Found
- `UserAlreadyExists` → 400 Bad Request
- `ValidationError` → 422 Unprocessable Entity
- `BusinessRuleViolation` → 400 Bad Request

## Usage Guidelines

### Service Layer

Services should raise domain exceptions:

```python
class UserService:
    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)
        return UserResponse(**user.model_dump())
```

### HTTP Layer

The HTTP layer automatically converts exceptions to responses:

```python
@router.get("/{user_id}")
async def get_user(user_id: str, service: UserService = Depends()):
    # No try/catch needed - exception handlers do the conversion
    return await service.get_user(user_id)
```

### Repository Layer

Repositories can raise infrastructure exceptions:

```python
class UserRepository:
    async def get_by_id(self, user_id: str) -> User | None:
        try:
            return await User.find_one({"id": user_id})
        except ConnectionError as e:
            raise DatabaseConnectionError(str(e))
```

## Best Practices

### 1. Use Specific Exceptions

```python
# Good
raise UserNotFound(user_id=user_id)

# Bad
raise DomainException("User not found")
```

### 2. Include Context

```python
# Good
raise BusinessRuleViolation(
    rule="max_login_attempts",
    message="Too many failed login attempts",
    context={"attempts": 5, "max_allowed": 3}
)

# Bad
raise BusinessRuleViolation("max_login_attempts", "Failed")
```

### 3. Layer Appropriate Exceptions

- **Service Layer**: Domain exceptions (`UserNotFound`, `ValidationError`)
- **Repository Layer**: Infrastructure exceptions (`DatabaseConnectionError`)
- **HTTP Layer**: No manual exception handling (use global handlers)

### 4. Don't Catch and Re-raise Generic Exceptions

```python
# Good
try:
    await self.repository.save(user)
except DatabaseConnectionError:
    raise BusinessRuleViolation(
        "data_persistence",
        "Unable to save user data"
    )

# Bad
try:
    await self.repository.save(user)
except Exception as e:
    raise DomainException(str(e))
```

## Error Response Format

HTTP responses follow a consistent format:

```json
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

## Testing

Test exceptions by verifying the specific exception type and attributes:

```python
async def test_user_not_found():
    with pytest.raises(UserNotFound) as exc_info:
        await service.get_user("nonexistent")

    assert exc_info.value.error_code == "USER_NOT_FOUND_BY_ID"
    assert "nonexistent" in exc_info.value.message
```

## Adding New Exceptions

1. **Determine the domain**: User, Order, Payment, etc.
2. **Choose the appropriate file**: Create new domain file if needed
3. **Inherit from the right base**: Domain-specific base class
4. **Include error code**: Machine-readable identifier
5. **Add context attributes**: Relevant data for debugging
6. **Update `__init__.py`**: Export the new exception
7. **Add handler if needed**: Custom HTTP status code mapping

Example:

```python
# app/exceptions/order.py
class OrderNotFound(DomainException):
    def __init__(self, order_id: str):
        message = f"Order '{order_id}' not found"
        error_code = "ORDER_NOT_FOUND"

        self.order_id = order_id
        super().__init__(message, error_code)
```

## Migration from Old Exception System

When migrating from generic `HTTPException` usage:

1. **Identify the domain**: What business concept is involved?
2. **Choose specific exception**: Use domain-specific exceptions
3. **Remove HTTP details**: No status codes in service layer
4. **Update tests**: Test domain exceptions, not HTTP responses
5. **Add context**: Include relevant business data

This exception system provides clear separation of concerns, better testability, and consistent error handling across the entire application.
