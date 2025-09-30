# Database Documentation

## Overview

This application uses a **dual database architecture** combining PostgreSQL (relational) and MongoDB (document) databases. This hybrid approach allows optimal data storage based on data structure and access patterns.

## Technology Stack

### PostgreSQL (SQL)
- **Database**: PostgreSQL 16+
- **ORM**: SQLModel (type-safe SQL operations)
- **Migrations**: Alembic (schema versioning)
- **Driver**: AsyncPG (async Python driver)
- **Connection**: Async connection pooling via SQLAlchemy

### MongoDB (NoSQL)
- **Database**: MongoDB 7.0+
- **Driver**: Motor (async Python driver)
- **ODM**: Beanie (async ODM built on Pydantic)
- **Connection**: Async connection pooling

## When to Use Which Database

### Use PostgreSQL for:
- Structured data with relationships (foreign keys)
- Data requiring ACID transactions
- Complex queries with JOINs
- Data that changes schema infrequently
- Reporting and analytics

### Use MongoDB for:
- Flexible/dynamic schemas
- Nested/hierarchical data structures
- High-volume read operations
- Rapidly evolving data models
- Document-based data

## Database Configuration

### Connection Settings

```python
# app/configs/app.py
class AppConfig(BaseSettings):
    # PostgreSQL
    postgre_database_url: str = "postgresql+asyncpg://admin:password@localhost:5432/database_develop"

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "app_db"
    mongodb_test_database: str = "test_db"

    class Config:
        env_file = ".env"
```

### Environment Variables

```env
# PostgreSQL
POSTGRE_DATABASE_URL=postgresql+asyncpg://admin:password@postgresql:5432/database_develop

# MongoDB
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DATABASE=app_db
MONGODB_TEST_DATABASE=test_db
```

### Unified Connection Management

Both databases are managed through a unified lifespan context manager:

```python
# app/dependencies/lifespan.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize both databases
    await nosql_db_manager.connect()  # MongoDB
    await sql_db_manager.connect()     # PostgreSQL

    yield  # Application runs

    # Shutdown: Close both connections
    await nosql_db_manager.close()
    await sql_db_manager.close()
```

## Schema Design

### PostgreSQL Models (SQLModel)

All SQL models inherit from `BaseModel` providing common audit fields:

```python
# app/internal/models/sql/base.py
class BaseModel(SQLModel, table=False):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)
    deleted_by: Optional[str] = Field(default=None)

    def soft_delete(self, deleted_by: Optional[str] = None):
        self.deleted_at = datetime.now()
        self.deleted_by = deleted_by

    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

**User Table Example:**
```python
# app/internal/models/sql/user.py
class User(BaseModel, table=True):
    __tablename__ = "users"

    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
```

### MongoDB Models (Beanie)

All NoSQL models inherit from `BaseEntity` (Beanie Document):

```python
# app/internal/models/no_sql/base.py
class BaseEntity(Document):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None)
    updated_at: Optional[datetime] = Field(None)
    updated_by: Optional[str] = Field(None)
    deleted_at: Optional[datetime] = Field(None)
    deleted_by: Optional[str] = Field(None)

    def soft_delete(self, deleted_by: Optional[str] = None):
        self.deleted_at = datetime.now()
        self.deleted_by = deleted_by

    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

**User Collection Example:**
```python
# app/internal/models/no_sql/user.py
class User(BaseEntity):
    email: Indexed(str, unique=True) = Field(...)
    username: Indexed(str, unique=True) = Field(...)
    full_name: Optional[str] = Field(None)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True),
            IndexModel([("username", 1)], unique=True),
        ]
```

## Data Types and Validation

### Field Types

- **UUID**: For unique identifiers
- **datetime**: Timezone-aware timestamps
- **str**: Text fields with length constraints
- **bool**: Boolean flags
- **Optional**: Nullable fields

### Validation Rules

```python
# Email validation
email: Indexed(str, unique=True) = Field(
    ...,
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Username validation
username: Indexed(str, unique=True) = Field(
    ...,
    min_length=3,
    max_length=50,
    regex=r'^[a-zA-Z0-9_]+$'
)

# Password validation (in DTO)
password: str = Field(..., min_length=8)
```

## PostgreSQL Migrations (Alembic)

### Migration Workflow

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
app/databases/sql/migrations/
├── env.py                    # Alembic environment config
├── versions/
│   └── 20250930_xxxx_description.py  # Migration files
└── alembic.ini               # Alembic configuration
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

## Indexing Strategy

### PostgreSQL Indexes

Indexes are created via Alembic migrations:

```python
# In migration file
def upgrade():
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_created_at', 'users', ['created_at'])
```

### MongoDB Indexes

Beanie automatically creates indexes based on model definitions:

```python
# Single field indexes
email: Indexed(str, unique=True)  # Unique index on email
username: Indexed(str, unique=True)  # Unique index on username

# Compound indexes via Settings
class Settings:
    indexes = [
        IndexModel([("email", 1)], unique=True),
        IndexModel([("created_at", -1)]),  # Descending for latest first
        IndexModel([("deleted_at", 1)]),   # For soft deletion queries
    ]
```

### Index Performance

- **Query optimization**: Indexes speed up common queries
- **Unique constraints**: Prevent duplicate data
- **Sorting**: Indexes support efficient sorting
- **Filtering**: Indexes optimize WHERE clauses

## Repository Pattern

### Base Repository

```python
class BaseRepository:
    def __init__(self, model_class):
        self.model = model_class

    async def create(self, data: dict):
        instance = self.model(**data)
        await instance.save()
        return instance

    async def get_by_id(self, id: UUID) -> Optional[Document]:
        return await self.model.find_one({"id": id, "deleted_at": None})

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        return await self.model.find({"deleted_at": None}).skip(skip).limit(limit).to_list()

    async def update(self, id: UUID, data: dict):
        await self.model.find_one({"id": id}).update({"$set": data})
        return await self.get_by_id(id)

    async def delete(self, id: UUID):
        instance = await self.get_by_id(id)
        if instance:
            instance.soft_delete()
            await instance.save()
        return instance
```

### User Repository

```python
class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.model.find_one({"email": email, "deleted_at": None})

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.model.find_one({"username": username, "deleted_at": None})

    async def email_exists(self, email: str) -> bool:
        user = await self.model.find_one({"email": email, "deleted_at": None})
        return user is not None

    async def username_exists(self, username: str) -> bool:
        user = await self.model.find_one({"username": username, "deleted_at": None})
        return user is not None
```

## Query Patterns

### Basic Queries

```python
# Find by ID
user = await User.find_one({"id": user_id, "deleted_at": None})

# Find all active users
users = await User.find({"is_active": True, "deleted_at": None}).to_list()

# Find with pagination
users = await User.find({"deleted_at": None}).skip(10).limit(20).to_list()

# Find with sorting
users = await User.find({"deleted_at": None}).sort(-User.created_at).to_list()
```

### Complex Queries

```python
# Find users created in the last 30 days
from datetime import datetime, timedelta

thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
recent_users = await User.find({
    "created_at": {"$gte": thirty_days_ago},
    "deleted_at": None
}).to_list()

# Find users by email domain
gmail_users = await User.find({
    "email": {"$regex": r"@gmail\.com$"},
    "deleted_at": None
}).to_list()

# Count active users
active_count = await User.find({"is_active": True, "deleted_at": None}).count()
```

### Aggregation Queries

```python
# Count users by status
pipeline = [
    {"$match": {"deleted_at": None}},
    {"$group": {"_id": "$is_active", "count": {"$sum": 1}}}
]
result = await User.aggregate(pipeline).to_list()

# Users created per day
pipeline = [
    {"$match": {"deleted_at": None}},
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
        "count": {"$sum": 1}
    }},
    {"$sort": {"_id": 1}}
]
daily_counts = await User.aggregate(pipeline).to_list()
```

## Data Operations

### Create Operations

```python
# Create new user
user_data = {
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "password_hash": "hashed_password",
    "is_active": True
}
user = User(**user_data)
await user.save()
```

### Read Operations

```python
# Get single user
user = await User.get(user_id)

# Get multiple users
users = await User.find({"is_active": True}).to_list()

# Get with conditions
user = await User.find_one({"email": "user@example.com"})
```

### Update Operations

```python
# Update single field
await user.update({"$set": {"full_name": "New Name"}})

# Update multiple fields
await user.update({"$set": {
    "full_name": "New Name",
    "updated_at": datetime.now(timezone.utc)
}})

# Update with conditions
await User.find({"is_active": False}).update({"$set": {"is_active": True}})
```

### Delete Operations

```python
# Soft delete (preferred)
user.soft_delete()
await user.save()

# Hard delete (use with caution)
await user.delete()

# Bulk soft delete
await User.find({"is_active": False}).update({"$set": {
    "deleted_at": datetime.now(timezone.utc)
}})
```

## Audit Trail

### Automatic Tracking

All entities automatically track:
- **Creation**: `created_at`, `created_by`
- **Updates**: `updated_at`, `updated_by`
- **Deletion**: `deleted_at`, `deleted_by`

### Implementation

```python
def set_audit_fields(self, user_id: Optional[UUID] = None):
    now = utc_now()
    if not self.id:  # New document
        self.created_at = now
        self.created_by = user_id
    self.updated_at = now
    self.updated_by = user_id
```

### Querying Audit Data

```python
# Find all changes by user
changes = await User.find({"updated_by": user_id}).to_list()

# Find recently modified users
recent_changes = await User.find({
    "updated_at": {"$gte": datetime.now(timezone.utc) - timedelta(hours=24)}
}).to_list()
```

## Soft Deletion

### Implementation

```python
@property
def is_deleted(self) -> bool:
    return self.deleted_at is not None

def soft_delete(self, deleted_by: Optional[UUID] = None):
    now = utc_now()
    self.deleted_at = now
    self.deleted_by = deleted_by
    self.updated_at = now
    self.updated_by = deleted_by
```

### Querying Non-Deleted Records

```python
# Always include deleted_at filter
active_users = await User.find({"deleted_at": None}).to_list()

# Repository pattern handles this automatically
users = await user_repository.get_all()  # Only non-deleted
```

## Migration Strategy

### Schema Changes

```python
# Migration script example
async def migrate_add_field():
    await User.find({}).update({"$set": {"new_field": "default_value"}})

# Index changes
async def migrate_add_index():
    await User.create_indexes()
```

### Data Migrations

```python
# Data transformation example
async def migrate_email_lowercase():
    users = await User.find({}).to_list()
    for user in users:
        user.email = user.email.lower()
        await user.save()
```

## Performance Optimization

### Connection Pooling

```python
# Motor connection pool settings
client = AsyncIOMotorClient(
    mongodb_url,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=5000
)
```

### Query Optimization

```python
# Use projection to limit fields
users = await User.find({"is_active": True}, {"email": 1, "username": 1}).to_list()

# Use explain() for query analysis
query = User.find({"email": "user@example.com"})
explanation = await query.explain()
```

### Batch Operations

```python
# Bulk insert
users_data = [{"email": f"user{i}@example.com", "username": f"user{i}"} for i in range(100)]
await User.insert_many([User(**data) for data in users_data])

# Bulk update
await User.find({"is_active": False}).update({"$set": {"is_active": True}})
```

## Backup and Recovery

### Database Backup

```bash
# MongoDB dump
mongodump --uri="mongodb://localhost:27017/app_db" --out=/backup/

# Restore
mongorestore --uri="mongodb://localhost:27017/app_db" /backup/app_db/
```

### Docker Backup

```bash
# Backup MongoDB data volume
docker run --rm -v backend-fastapi-app_mongodb_data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb_backup.tar.gz /data

# Restore
docker run --rm -v backend-fastapi-app_mongodb_data:/data -v $(pwd):/backup alpine tar xzf /backup/mongodb_backup.tar.gz -C /
```

## Testing with Database

### Test Database Setup

```python
# Test configuration
class TestDatabaseSettings(DatabaseSettings):
    mongodb_db_name: str = "test_db"

# Test fixtures
@pytest.fixture
async def test_db():
    await init_database(test=True)
    yield
    await User.delete_all()  # Clean up
```

### Test Data Creation

```python
# Test user factory
async def create_test_user(**kwargs):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password_hash": "hashed_password",
        "is_active": True,
        **kwargs
    }
    user = User(**user_data)
    await user.save()
    return user
```

## Monitoring and Maintenance

### Database Monitoring

```python
# Connection status
async def check_database_health():
    try:
        await User.find_one({})
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Performance Metrics

```python
# Query performance
async def get_query_stats():
    stats = await User.get_motor_collection().index_information()
    return stats
```

### Maintenance Tasks

```python
# Clean up old soft-deleted records
async def cleanup_old_deleted_records():
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)
    await User.find({
        "deleted_at": {"$lt": cutoff_date}
    }).delete()
```

## Security Considerations

### Data Protection

- **Password hashing**: Never store plain text passwords
- **Sensitive data**: Exclude from API responses
- **Access control**: Implement proper authentication
- **Data encryption**: MongoDB encryption at rest

### Query Security

- **Input validation**: Pydantic models prevent injection
- **Parameterized queries**: Beanie handles query building
- **Access patterns**: Repository pattern controls data access

### Audit Security

- **Immutable audit**: Audit fields should not be modifiable
- **Retention policy**: Define how long to keep audit data
- **Access logging**: Track who accesses audit information
