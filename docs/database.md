# Database Documentation

## Overview

This application uses a **dual database architecture** combining PostgreSQL (relational) and MongoDB (document) databases. This hybrid approach allows optimal data storage based on data structure and access patterns.

## Database Strategy

### PostgreSQL (User Entity)

- **Database**: PostgreSQL 16+
- **ORM**: SQLModel (type-safe SQL operations)
- **Migrations**: Alembic (schema versioning)
- **Driver**: AsyncPG (async Python driver)
- **Use Case**: User entity with structured data and ACID requirements

### MongoDB (Log Entity)

- **Database**: MongoDB 7.0+
- **Driver**: Motor (async Python driver)
- **ODM**: Beanie (async ODM built on Pydantic)
- **Use Case**: Audit logs with flexible schema and high write throughput

## When to Use Which Database

### Use PostgreSQL for:

- Structured data with relationships (foreign keys)
- Data requiring ACID transactions
- Complex queries with JOINs
- Data that changes schema infrequently
- Entities with strict validation requirements

### Use MongoDB for:

- Flexible/dynamic schemas
- Nested/hierarchical data structures
- High-volume write operations
- Audit trails and event logs
- Rapidly evolving data models

## Database Configuration

### Connection Settings

```python
# app/infrastructure/configs/app.py
class AppConfig(BaseSettings):
    # PostgreSQL
    postgre_database_url: str = "postgresql+asyncpg://admin:password@localhost:5432/database_develop"

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "backend_fastapi_app_dev"
    mongodb_test_db_name: str = "backend_fastapi_app_test"

    model_config = SettingsConfigDict(env_file=".env")
```

### Environment Variables

```env
# PostgreSQL
POSTGRE_DATABASE_URL=postgresql+asyncpg://admin:password@postgresql:5432/database_develop

# MongoDB
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=backend_fastapi_app_dev
MONGODB_TEST_DB_NAME=backend_fastapi_app_test
```

### Unified Connection Management

Both databases are managed through the infrastructure layer's lifespan context:

```python
# app/infrastructure/setup.py
@asynccontextmanager
async def clean_architecture_lifespan(app: FastAPI):
    # Startup: Initialize both databases
    await postgres_manager.connect()
    await mongodb_manager.connect()

    # Setup dependencies
    session = await postgres_manager.get_session()
    setup_dependencies(session)

    yield  # Application runs

    # Shutdown: Close both connections
    await postgres_manager.disconnect()
    await mongodb_manager.disconnect()
```

## PostgreSQL Schema

### User Model (SQLModel)

```python
# app/infrastructure/persistence/postgresql/models/user.py
class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    full_name: str | None = None
    is_active: bool = Field(default=True)

    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: str | None = None
    deleted_at: datetime | None = None
    deleted_by: str | None = None
```

### PostgreSQL Migrations (Alembic)

```bash
# Generate new migration after model changes
make migrate-generate MESSAGE="add user table"

# Apply migrations
make migrate-up

# Rollback one migration
make migrate-down

# View migration history
make migrate-history

# Check current version
make migrate-current
```

### Migration File Structure

```
app/infrastructure/persistence/postgresql/migrations/
├── env.py                    # Alembic environment config
├── script.py.mako            # Migration template
└── versions/
    └── 20250930_xxxx_description.py  # Migration files
```

### Database Seeding

```bash
# Seed PostgreSQL with sample data
make seed

# Clear seeded data
make seed-clear

# Reseed (clear + seed)
make reseed
```

## MongoDB Schema

### Log Model (Beanie)

```python
# app/infrastructure/persistence/mongodb/models/log.py
class LogModel(Document):
    id: UUID = Field(default_factory=uuid4)
    action: str = Field(...)
    user_id: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "logs"
        indexes = [
            IndexModel([("user_id", 1)]),
            IndexModel([("action", 1)]),
            IndexModel([("created_at", -1)]),
        ]
```

### MongoDB Indexes

Beanie automatically creates indexes based on model definitions:

```python
class Settings:
    indexes = [
        IndexModel([("user_id", 1)]),           # Ascending index
        IndexModel([("created_at", -1)]),       # Descending index
        IndexModel([("email", 1)], unique=True), # Unique index
    ]
```

## Repository Pattern

### Domain Repository Interfaces

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

### PostgreSQL Repository Implementation

```python
# app/infrastructure/persistence/postgresql/repositories/user_write.py
class PostgresUserWriteRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, aggregate: UserAggregate) -> None:
        model = UserMapper.to_model(aggregate)
        existing = await self._session.get(UserModel, model.id)

        if existing:
            UserMapper.update_model(existing, aggregate)
            await self._session.commit()
        else:
            self._session.add(model)
            await self._session.commit()

    async def exists_by_email(self, email: Email) -> bool:
        stmt = select(UserModel).where(
            UserModel.email == str(email),
            UserModel.deleted_at.is_(None)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
```

### MongoDB Repository Implementation

```python
# app/infrastructure/persistence/mongodb/repositories/log_write.py
class MongoLogWriteRepository:
    async def save(self, aggregate: LogAggregate) -> None:
        model = LogMapper.to_model(aggregate)
        await model.save()

    async def delete(self, aggregate: LogAggregate) -> None:
        aggregate.soft_delete()
        await self.save(aggregate)
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
            deleted_at=user.deleted_at,
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
        user.created_at = model.created_at
        user.updated_at = model.updated_at
        user.deleted_at = model.deleted_at
        return UserAggregate.reconstitute(user)

    @staticmethod
    def to_read_model(model: UserModel) -> UserReadModel:
        return UserReadModel(
            id=str(model.id),
            email=model.email,
            username=model.username,
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
```

## Query Patterns

### PostgreSQL Queries

```python
# Basic query
stmt = select(UserModel).where(UserModel.id == user_id)
result = await session.execute(stmt)
user = result.scalar_one_or_none()

# Pagination
stmt = select(UserModel).where(
    UserModel.deleted_at.is_(None)
).offset(skip).limit(limit)
result = await session.execute(stmt)
users = result.scalars().all()

# Count
stmt = select(func.count()).select_from(UserModel).where(
    UserModel.deleted_at.is_(None)
)
result = await session.execute(stmt)
count = result.scalar_one()
```

### MongoDB Queries

```python
# Find by ID
log = await LogModel.find_one(LogModel.id == log_id)

# Find with pagination
logs = await LogModel.find(
    LogModel.deleted_at == None
).skip(skip).limit(limit).to_list()

# Find by user
logs = await LogModel.find(
    LogModel.user_id == user_id
).sort(-LogModel.created_at).to_list()

# Aggregation
pipeline = [
    {"$match": {"deleted_at": None}},
    {"$group": {"_id": "$action", "count": {"$sum": 1}}}
]
result = await LogModel.aggregate(pipeline).to_list()
```

## Audit Trail

### Automatic Tracking

All entities automatically track:
- **Creation**: `created_at`, `created_by`
- **Updates**: `updated_at`, `updated_by`
- **Deletion**: `deleted_at`, `deleted_by`

### Implementation

```python
# Domain entity with audit fields
class BaseEntity:
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: str | None = None
    deleted_at: datetime | None = None
    deleted_by: str | None = None

    def soft_delete(self, deleted_by: str | None = None) -> None:
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

## Soft Deletion

### Pattern

Records are never hard-deleted. Instead, they're marked with `deleted_at`:

```python
# Soft delete
async def delete(self, aggregate: UserAggregate) -> None:
    aggregate.soft_delete()
    await self.save(aggregate)

# Query non-deleted records
async def list_all(self, skip: int, limit: int) -> list[UserAggregate]:
    stmt = select(UserModel).where(
        UserModel.deleted_at.is_(None)  # Only non-deleted
    ).offset(skip).limit(limit)
    ...
```

## Event-Driven Synchronization

Domain events synchronize data between databases:

```
User Created (PostgreSQL)
    ↓
UserCreated Event Published
    ↓
UserEventHandler receives event
    ↓
CreateLogCommand executed
    ↓
Log Created (MongoDB)
```

```python
# Event handler creates audit log
class UserEventHandler:
    async def on_user_created(self, event: UserCreated) -> None:
        command = CreateLogCommand(
            action="USER_CREATED",
            user_id=event.user_id,
            metadata={"email": event.email, "username": event.username},
        )
        await self._log_handler.handle(command)
```

## Database Management Commands

```bash
# Both databases
make db-up         # Start both
make db-down       # Stop both
make db-reset      # Reset all data

# PostgreSQL
make postgres-up   # Start PostgreSQL
make postgres-down # Stop PostgreSQL
make shell-postgres # Access PostgreSQL shell
make migrate-up    # Apply migrations
make seed          # Seed data

# MongoDB
make mongo-up      # Start MongoDB
make mongo-down    # Stop MongoDB
make shell-mongo   # Access MongoDB shell

# Test databases
make setup-test-db    # Setup test databases
make test-db-reset    # Reset test databases
```

## Performance Optimization

### Connection Pooling

```python
# PostgreSQL connection pool
engine = create_async_engine(
    database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# MongoDB connection pool
client = AsyncIOMotorClient(
    mongodb_url,
    maxPoolSize=50,
    minPoolSize=10,
)
```

### Indexing Strategy

PostgreSQL indexes via migrations:

```python
def upgrade():
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])
```

MongoDB indexes via model settings:

```python
class Settings:
    indexes = [
        IndexModel([("email", 1)], unique=True),
        IndexModel([("created_at", -1)]),
    ]
```

## Testing with Databases

### Unit Tests

Mock repositories for fast tests:

```python
@pytest.fixture
def mock_repository():
    return AsyncMock(spec=IUserRepository)

async def test_create_user(mock_repository):
    mock_repository.exists_by_email.return_value = False
    handler = CreateUserHandler(mock_repository, ...)
    result = await handler.handle(command)
    assert result is not None
```

### Integration Tests

Use testcontainers for isolated tests:

```python
@pytest.fixture
async def postgres_session():
    # Testcontainers creates isolated PostgreSQL
    async with AsyncSession(engine) as session:
        yield session
```

### E2E Tests

Use separate test databases:

```python
# Test databases on running Docker services
POSTGRE_DATABASE_URL=...database_test
MONGODB_DB_NAME=backend_fastapi_app_test
```

## Security Considerations

### Data Protection

- **Password hashing**: Never store plain text passwords
- **Sensitive data**: Excluded from API responses
- **Access control**: Implement proper authentication

### Query Security

- **Input validation**: Pydantic models and Value Objects
- **Parameterized queries**: SQLAlchemy handles query building
- **Access patterns**: Repository pattern controls data access
