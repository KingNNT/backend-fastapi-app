# Architecture Documentation

## Overview

This FastAPI application follows **Clean Architecture** with **Domain-Driven Design (DDD)** tactical patterns and **CQRS (Command Query Responsibility Segregation)**. The architecture ensures maintainability, testability, and scalability through clear layer separation and dependency inversion.

## Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│              (FastAPI Controllers + DTOs)                    │
│   • REST API controllers with version management             │
│   • Request/Response DTOs                                    │
│   • FastAPI dependency injection                             │
├─────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                         │
│                (Commands + Queries + Handlers)               │
│   • CQRS command handlers (write operations)                 │
│   • CQRS query handlers (read operations)                    │
│   • Read models for optimized queries                        │
├─────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                            │
│         (Aggregates + Entities + Value Objects)              │
│   • Domain aggregates (consistency boundaries)               │
│   • Entities with identity and lifecycle                     │
│   • Value objects (immutable, self-validating)               │
│   • Domain events                                            │
│   • Repository interfaces (Protocols)                        │
├─────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE LAYER                       │
│            (Databases + Event Bus + Mappers)                 │
│   • PostgreSQL repository implementations                    │
│   • MongoDB repository implementations                       │
│   • In-memory event bus                                      │
│   • Entity-Model mappers                                     │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
app/
├── core/                          # INNER LAYERS (no framework dependencies)
│   ├── domain/                    # Layer 1: DOMAIN (DDD patterns)
│   │   ├── aggregates/            # Aggregate roots
│   │   │   ├── user.py            # UserAggregate
│   │   │   └── log.py             # LogAggregate
│   │   ├── entities/              # Domain entities with identity
│   │   │   ├── base.py            # BaseEntity with audit trail
│   │   │   ├── user.py            # User entity
│   │   │   └── log.py             # Log entity
│   │   ├── value_objects/         # Immutable self-validating objects
│   │   │   ├── email.py           # Email value object
│   │   │   ├── username.py        # Username value object
│   │   │   ├── user_id.py         # UserId value object
│   │   │   └── log_id.py          # LogId value object
│   │   ├── events/                # Domain events
│   │   │   ├── base.py            # BaseDomainEvent
│   │   │   ├── user_events.py     # UserCreated, UserUpdated, etc.
│   │   │   └── log_events.py      # Log events
│   │   ├── specifications/        # Business rules
│   │   ├── services/              # Domain services
│   │   │   └── user_service.py    # UserDomainService
│   │   ├── repositories/          # Repository interfaces (Protocols)
│   │   │   └── user.py            # IUserRepository, IUserWriteRepository
│   │   └── exceptions/            # Domain exceptions
│   │       ├── base.py            # DomainException
│   │       ├── error_codes.py     # ErrorCode enum
│   │       └── user.py            # UserNotFound, UserAlreadyExists
│   │
│   └── application/               # Layer 2: APPLICATION (CQRS)
│       ├── commands/              # Write side
│       │   ├── user/              # User commands
│       │   │   ├── create_user.py # CreateUserCommand
│       │   │   ├── update_user.py # UpdateUserCommand
│       │   │   └── delete_user.py # DeleteUserCommand
│       │   ├── log/               # Log commands
│       │   └── handlers/          # Command handlers
│       │       └── user_handlers.py
│       ├── queries/               # Read side
│       │   ├── user/              # User queries
│       │   │   ├── get_user.py    # GetUserByIdQuery, GetUserByEmailQuery
│       │   │   └── list_users.py  # ListUsersQuery
│       │   ├── log/               # Log queries
│       │   └── handlers/          # Query handlers
│       │       └── user_handlers.py
│       ├── read_models/           # Optimized read models
│       │   └── user.py            # UserReadModel
│       └── interfaces/            # Application interfaces
│           └── event_bus.py       # IEventBus
│
├── presentation/                  # Layer 3: PRESENTATION
│   ├── api/                       # REST API controllers
│   │   ├── v1/                    # API version 1
│   │   │   ├── user.py            # User endpoints
│   │   │   └── log.py             # Log endpoints
│   │   └── system.py              # Health & version endpoints
│   ├── dependencies/              # FastAPI dependency injection
│   │   ├── handlers.py            # Handler factory functions
│   │   ├── repositories.py        # Repository getters/setters
│   │   └── services.py            # Service getters
│   └── dtos/                      # Data Transfer Objects
│       ├── user.py                # UserCreateRequest, UserResponse
│       ├── log.py                 # Log DTOs
│       └── response.py            # Standard response shapes
│
├── infrastructure/                # Layer 4: INFRASTRUCTURE
│   ├── configs/                   # Configuration
│   │   ├── app.py                 # AppConfig (Pydantic Settings)
│   │   ├── logging.py             # Logging configuration
│   │   └── version.py             # Version management
│   ├── persistence/               # Database implementations
│   │   ├── postgresql/            # PostgreSQL (User entity)
│   │   │   ├── models/            # SQLModel ORM models
│   │   │   ├── repositories/      # Write/Read repositories
│   │   │   ├── mappers/           # Entity <-> Model mappers
│   │   │   ├── migrations/        # Alembic migrations
│   │   │   ├── seeds/             # Database seeding
│   │   │   └── database.py        # Connection manager
│   │   └── mongodb/               # MongoDB (Log entity)
│   │       ├── models/            # Beanie ODM models
│   │       ├── repositories/      # Write/Read repositories
│   │       ├── mappers/           # Entity <-> Model mappers
│   │       └── database.py        # Connection manager
│   ├── messaging/                 # Infrastructure services
│   │   ├── event_bus.py           # InMemoryEventBus
│   │   └── password_hasher.py     # Password hashing
│   ├── event_handlers/            # Domain event handlers
│   │   └── user_event_handlers.py # Creates audit logs
│   ├── web/                       # Web infrastructure
│   │   ├── middleware.py          # Request logging, security headers
│   │   ├── exception_handlers.py  # Domain exception -> HTTP response
│   │   └── response.py            # APIResponse utility
│   └── setup.py                   # Dependency injection setup
│
└── main.py                        # Application entry point

tests/                             # Test suite (outside app/)
├── unit/                          # Unit tests with mocked dependencies
│   ├── domain/                    # Domain layer tests
│   └── application/               # Application layer tests
├── integration/                   # Integration tests (testcontainers)
├── e2e/                           # End-to-end tests
└── conftest.py                    # Shared test fixtures
```

## Domain-Driven Design Patterns

### 1. Value Objects

Immutable, self-validating objects that represent domain concepts:

```python
# app/core/domain/value_objects/email.py
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValidationError("email", self.value, "Invalid email format")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @property
    def domain(self) -> str:
        return self.value.split('@')[1]

    def __str__(self) -> str:
        return self.value
```

**Key Characteristics:**
- Frozen dataclasses (immutable)
- Self-validating in `__post_init__`
- Custom equality based on value
- No external dependencies

### 2. Entities

Objects with identity and lifecycle:

```python
# app/core/domain/entities/user.py
class User:
    def __init__(
        self,
        id: UserId,
        email: Email,
        username: Username,
        password_hash: str,
        full_name: str | None = None,
        is_active: bool = True,
    ):
        self.id = id
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.is_active = is_active
        # Audit fields from BaseEntity
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def update_email(self, new_email: Email) -> None:
        self.email = new_email
        self.updated_at = datetime.now(timezone.utc)
```

### 3. Aggregates

Consistency boundaries that manage entities and publish domain events:

```python
# app/core/domain/aggregates/user.py
class UserAggregate:
    def __init__(self, user: User):
        self._user = user
        self._events: list[BaseDomainEvent] = []

    @classmethod
    def create(
        cls,
        email: Email,
        username: Username,
        password_hash: str,
        full_name: str | None = None,
    ) -> "UserAggregate":
        user = User(
            id=UserId.generate(),
            email=email,
            username=username,
            password_hash=password_hash,
            full_name=full_name,
        )
        aggregate = cls(user)
        aggregate._events.append(UserCreated(
            user_id=str(user.id),
            email=str(email),
            username=str(username),
        ))
        return aggregate

    @classmethod
    def reconstitute(cls, user: User) -> "UserAggregate":
        """Restore aggregate from repository (no events)."""
        return cls(user)

    def update_email(self, new_email: Email) -> None:
        old_email = str(self._user.email)
        self._user.update_email(new_email)
        self._events.append(UserEmailUpdated(
            user_id=str(self._user.id),
            old_email=old_email,
            new_email=str(new_email),
        ))

    @property
    def events(self) -> list[BaseDomainEvent]:
        return self._events.copy()

    def clear_events(self) -> None:
        self._events.clear()
```

### 4. Domain Events

Record what happened in the domain:

```python
# app/core/domain/events/user_events.py
@dataclass(frozen=True)
class UserCreated(BaseDomainEvent):
    user_id: str
    email: str
    username: str

    def _payload(self) -> dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
        }

@dataclass(frozen=True)
class UserEmailUpdated(BaseDomainEvent):
    user_id: str
    old_email: str
    new_email: str
```

### 5. Repository Interfaces

Protocol-based interfaces for data access:

```python
# app/core/domain/repositories/user.py
from typing import Protocol

class IUserWriteRepository(Protocol):
    async def save(self, aggregate: UserAggregate) -> None: ...
    async def delete(self, aggregate: UserAggregate) -> None: ...
    async def exists_by_email(self, email: Email) -> bool: ...
    async def exists_by_username(self, username: Username) -> bool: ...

class IUserReadRepository(Protocol):
    async def get_by_id(self, user_id: UserId) -> UserAggregate | None: ...
    async def get_by_email(self, email: Email) -> UserAggregate | None: ...
    async def list_all(self, skip: int, limit: int) -> list[UserAggregate]: ...
    async def count(self) -> int: ...
```

### 6. Domain Services

Cross-entity business logic:

```python
# app/core/domain/services/user_service.py
class UserDomainService:
    def __init__(self, repository: IUserRepository):
        self._repository = repository

    async def validate_new_user(self, email: Email, username: Username) -> None:
        if await self._repository.exists_by_email(email):
            raise UserAlreadyExists("email", str(email))
        if await self._repository.exists_by_username(username):
            raise UserAlreadyExists("username", str(username))
```

## CQRS Pattern

### Command Side (Write Path)

```
HTTP Request → Controller → Command Handler → Aggregate → Write Repository → Database
                                    ↓
                            Domain Events → Event Bus → Event Handlers → Audit Log
```

**Command Example:**

```python
# app/core/application/commands/user/create_user.py
@dataclass(frozen=True)
class CreateUserCommand:
    email: str
    username: str
    password: str
    full_name: str | None = None

# app/core/application/commands/handlers/user_handlers.py
class CreateUserHandler:
    def __init__(
        self,
        repository: IUserRepository,
        domain_service: UserDomainService,
        event_bus: IEventBus,
        password_hasher: IPasswordHasher,
    ):
        self._repository = repository
        self._domain_service = domain_service
        self._event_bus = event_bus
        self._password_hasher = password_hasher

    async def handle(self, command: CreateUserCommand) -> str:
        # 1. Create value objects (validates format)
        email = Email(command.email)
        username = Username(command.username)

        # 2. Validate business rules
        await self._domain_service.validate_new_user(email, username)

        # 3. Hash password
        password_hash = self._password_hasher.hash(command.password)

        # 4. Create aggregate (raises UserCreated event)
        aggregate = UserAggregate.create(
            email=email,
            username=username,
            password_hash=password_hash,
            full_name=command.full_name,
        )

        # 5. Persist
        await self._repository.save(aggregate)

        # 6. Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)

        return str(aggregate.user.id)
```

### Query Side (Read Path)

```
HTTP Request → Controller → Query Handler → Read Model Repository → Database
```

**Query Example:**

```python
# app/core/application/queries/user/get_user.py
@dataclass(frozen=True)
class GetUserByIdQuery:
    user_id: str

# app/core/application/queries/handlers/user_handlers.py
class GetUserByIdHandler:
    def __init__(self, repository: IUserReadModelRepository):
        self._repository = repository

    async def handle(self, query: GetUserByIdQuery) -> UserReadModel | None:
        return await self._repository.get_by_id(query.user_id)
```

### Read Models

Optimized DTOs for query operations:

```python
# app/core/application/read_models/user.py
@dataclass
class UserReadModel:
    id: str
    email: str
    username: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "UserReadModel":
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)
```

## Event-Driven Architecture

### Event Bus

In-memory pub/sub for domain events:

```python
# app/infrastructure/messaging/event_bus.py
class InMemoryEventBus(IEventBus):
    def __init__(self):
        self._subscribers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: BaseDomainEvent) -> None:
        handlers = self._subscribers.get(type(event), [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")
```

### Event Handlers

React to domain events:

```python
# app/infrastructure/event_handlers/user_event_handlers.py
class UserEventHandler:
    def __init__(self, log_handler: CreateLogHandler):
        self._log_handler = log_handler

    async def on_user_created(self, event: UserCreated) -> None:
        command = CreateLogCommand(
            action="USER_CREATED",
            user_id=event.user_id,
            metadata={"email": event.email, "username": event.username},
        )
        await self._log_handler.handle(command)
```

## Dependency Injection

### Setter Functions

Runtime configuration for dependencies:

```python
# app/presentation/dependencies/repositories.py
_user_repository: IUserRepository | None = None

def set_user_repository(repo: IUserRepository) -> None:
    global _user_repository
    _user_repository = repo

def get_user_repository() -> IUserRepository:
    if _user_repository is None:
        raise RuntimeError("User repository not initialized")
    return _user_repository
```

### Handler Factories

FastAPI dependency injection:

```python
# app/presentation/dependencies/handlers.py
def get_create_user_handler(
    repository: IUserRepository = Depends(get_user_repository),
    domain_service: UserDomainService = Depends(get_user_domain_service),
    event_bus: IEventBus = Depends(get_event_bus),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> CreateUserHandler:
    return CreateUserHandler(repository, domain_service, event_bus, password_hasher)

# Type alias for cleaner endpoint signatures
CreateUserHandlerDep = Annotated[CreateUserHandler, Depends(get_create_user_handler)]
```

### Lifespan Setup

Initialize dependencies at startup:

```python
# app/infrastructure/setup.py
@asynccontextmanager
async def clean_architecture_lifespan(app: FastAPI):
    # Startup
    await postgres_manager.connect()
    await mongodb_manager.connect()

    session = await postgres_manager.get_session()
    setup_dependencies(session)

    yield

    # Shutdown
    await postgres_manager.disconnect()
    await mongodb_manager.disconnect()

def setup_dependencies(session: AsyncSession) -> None:
    # Create repositories
    user_write_repo = PostgresUserWriteRepository(session)
    user_read_repo = PostgresUserReadRepository(session)
    combined_repo = CombinedUserRepository(user_write_repo, user_read_repo)

    # Create infrastructure services
    event_bus = InMemoryEventBus()
    password_hasher = SimplePasswordHasher()

    # Create event handlers and subscribe
    log_handler = CreateLogHandler(...)
    user_event_handler = UserEventHandler(log_handler)
    event_bus.subscribe(UserCreated, user_event_handler.on_user_created)
    event_bus.subscribe(UserUpdated, user_event_handler.on_user_updated)

    # Set dependencies
    set_user_repository(combined_repo)
    set_event_bus(event_bus)
    set_password_hasher(password_hasher)
```

## Data Flow Examples

### Creating a User (Complete Flow)

```
1. HTTP POST /v1/users/
   ↓
2. Presentation: create_user() receives UserCreateRequest
   ↓
3. Create CreateUserCommand with request data
   ↓
4. FastAPI injects CreateUserHandler (via dependency)
   ↓
5. Application: CreateUserHandler.handle(command)
   ↓
6. Create Email, Username value objects (validate format)
   ↓
7. Call UserDomainService.validate_new_user() (check uniqueness)
   ↓
8. Hash password via SimplePasswordHasher
   ↓
9. Domain: UserAggregate.create() creates entity with UserCreated event
   ↓
10. Infrastructure: PostgresUserWriteRepository.save(aggregate)
    - Convert aggregate to SQLModel
    - INSERT into PostgreSQL
    ↓
11. Application: Publish all events via InMemoryEventBus
    ↓
12. Infrastructure: UserEventHandler receives UserCreated event
    - Create CreateLogCommand
    - Save log to MongoDB
    ↓
13. Return 201 Created with user_id
```

### Querying a User

```
1. HTTP GET /v1/users/{id}
   ↓
2. Presentation: get_user() receives user_id
   ↓
3. Create GetUserByIdQuery(user_id)
   ↓
4. FastAPI injects GetUserByIdHandler
   ↓
5. Application: GetUserByIdHandler.handle(query)
   ↓
6. Infrastructure: PostgresUserReadModelRepository.get_by_id()
    - SELECT from PostgreSQL
    - Convert to UserReadModel
   ↓
7. Return UserReadModel
   ↓
8. Presentation: Serialize to JSON response
```

## Error Handling

### Domain Exceptions

```python
# app/core/domain/exceptions/user.py
class UserNotFound(DomainException):
    def __init__(self, user_id: str | None = None, email: str | None = None):
        super().__init__(
            error_code=ErrorCode.USER_NOT_FOUND,
            message=f"User not found",
            context={"user_id": user_id, "email": email},
        )

class UserAlreadyExists(DomainException):
    def __init__(self, field_name: str, field_value: str):
        super().__init__(
            error_code=ErrorCode.USER_ALREADY_EXISTS,
            message=f"User with {field_name} '{field_value}' already exists",
            context={"field": field_name, "value": field_value},
        )
```

### Exception Handlers

Convert domain exceptions to HTTP responses:

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

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code.value,
                "context": exc.context,
            },
        )
```

## Mapper Pattern

Convert between domain entities and persistence models:

```python
# app/infrastructure/persistence/postgresql/mappers/user.py
class UserMapper:
    @staticmethod
    def to_model(aggregate: UserAggregate) -> UserModel:
        user = aggregate.user
        return UserModel(
            id=user.id.value,
            email=str(user.email),
            username=str(user.username),
            password_hash=user.password_hash,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def to_aggregate(model: UserModel) -> UserAggregate:
        user = User(
            id=UserId(model.id),
            email=Email(model.email),
            username=Username(model.username),
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_active=model.is_active,
        )
        return UserAggregate.reconstitute(user)
```

## Testing Strategy

### Unit Tests

Test domain logic in isolation:

```python
# tests/unit/domain/test_aggregates.py
class TestUserAggregate:
    def test_create_raises_user_created_event(self):
        aggregate = UserAggregate.create(
            email=Email("test@example.com"),
            username=Username("testuser"),
            password_hash="hashed",
        )

        assert len(aggregate.events) == 1
        assert isinstance(aggregate.events[0], UserCreated)
```

### Integration Tests

Test with real databases via testcontainers:

```python
# tests/integration/postgresql/test_user_repository.py
async def test_save_and_retrieve_user(postgres_session):
    repository = PostgresUserRepository(postgres_session)
    aggregate = UserAggregate.create(...)

    await repository.save(aggregate)
    retrieved = await repository.get_by_id(aggregate.user.id)

    assert retrieved is not None
    assert retrieved.user.email == aggregate.user.email
```

### E2E Tests

Test full API flows:

```python
# tests/e2e/test_user_api.py
async def test_create_and_get_user(test_client):
    # Create
    response = await test_client.post("/v1/users/", json={...})
    assert response.status_code == 201
    user_id = response.json()["data"]["id"]

    # Get
    response = await test_client.get(f"/v1/users/{user_id}")
    assert response.status_code == 200
```

## Key Architectural Decisions

### 1. Dual Database Strategy

- **PostgreSQL**: User entity (ACID, relational, structured)
- **MongoDB**: Log entity (audit trail, flexible schema)
- Synchronized via domain events

### 2. Protocol-based Interfaces

- No inheritance required
- Structural typing for loose coupling
- Easy to swap implementations

### 3. Separate Read/Write Repositories

- Optimized for different access patterns
- Read models can be cached independently
- Write models ensure consistency

### 4. In-Memory Event Bus

- Simple and synchronous for now
- Can be replaced with message queue later
- Decouples business operations from side effects

### 5. Soft Deletion

- No hard deletes (data preservation)
- Audit trail maintained
- Tracked via `deleted_at`, `deleted_by`

This architecture provides a solid foundation for building scalable, maintainable applications following enterprise patterns and clean code principles.
