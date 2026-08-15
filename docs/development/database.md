# Database Management

## Overview

SQLite database with SQLAlchemy ORM, auto-seeding on first startup.

## Database File

```
data/catalog.db
```

## Connection

```python
# config.py
DATABASE_URL = "sqlite:///./data/catalog.db"

# database.py
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

## Session Management

```python
# database.py
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

## Initialization

```python
# database.py
def init_db():
    from university_catalog.models import Base
    Base.metadata.create_all(bind=get_engine())
```

Auto-runs on application startup via FastAPI lifespan.

## Seeding

```python
# data/seed.py
def seed_database():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    
    # Check if already seeded
    existing_dept = session.query(Department).first()
    if existing_dept:
        print("Database already seeded, skipping...")
        return
    
    # Insert departments, instructors, courses, prerequisites
    # ... seeding logic
    
    session.commit()
```

### Idempotency

```python
# Safe to run multiple times
seed_database()  # First run: seeds data
seed_database()  # Second run: prints "Database already seeded, skipping..."
```

## Schema Management

### Development (SQLite)

```bash
# Drop and recreate (loses data)
rm data/catalog.db
python -m uvicorn university_catalog.main:app

# Or programmatically
from university_catalog.database import init_db
from university_catalog.models import Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

### Production (PostgreSQL)

```bash
# Use Alembic for migrations
pip install alembic

# Initialize
alembic init alembic

# Configure alembic.ini with DATABASE_URL

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply
alembic upgrade head
```

## Querying

### Direct SQLAlchemy

```python
from university_catalog.database import get_db_session
from university_catalog.models import Course, Department

with get_db_session() as session:
    # Simple query
    courses = session.query(Course).all()
    
    # With joins
    courses = session.query(Course).join(Department).filter(
        Department.code == "CS"
    ).all()
    
    # Aggregation
    count = session.query(Course).filter(Course.department_id == 1).count()
```

### Repository Pattern (Recommended)

```python
from university_catalog.repositories import CourseRepository

with get_db_session() as session:
    repo = CourseRepository(session)
    courses = repo.search_courses("programming", department_code="CS")
```

## Common Operations

### Backup

```bash
# SQLite backup
sqlite3 data/catalog.db ".backup backup.db"

# Or copy file
cp data/catalog.db data/catalog.backup.db
```

### Restore

```bash
cp data/catalog.backup.db data/catalog.db
```

### Export Data

```bash
# CSV export
sqlite3 -header -csv data/catalog.db "SELECT * FROM courses" > courses.csv

# JSON export
sqlite3 -json data/catalog.db "SELECT * FROM courses" > courses.json
```

### Inspect Schema

```bash
sqlite3 data/catalog.db ".schema"

# Table info
sqlite3 data/catalog.db "PRAGMA table_info(courses)"

# Indexes
sqlite3 data/catalog.db "PRAGMA index_list(courses)"

# Foreign keys
sqlite3 data/catalog.db "PRAGMA foreign_key_list(courses)"
```

## Performance

### Indexes

```sql
-- Existing indexes
CREATE INDEX ix_courses_course_code ON courses(course_code);
CREATE INDEX ix_courses_title ON courses(title);
CREATE INDEX ix_courses_department_id ON courses(department_id);
CREATE INDEX ix_courses_instructor_id ON courses(instructor_id);
CREATE INDEX ix_instructors_name ON instructors(name);
CREATE INDEX ix_prerequisites_course_id ON prerequisites(course_id);
CREATE INDEX ix_prerequisites_prerequisite_id ON prerequisites(prerequisite_id);
```

### Analyze

```bash
sqlite3 data/catalog.db "ANALYZE;"
```

### Query Plan

```bash
sqlite3 data/catalog.db "EXPLAIN QUERY PLAN SELECT * FROM courses WHERE course_code = 'CS101';"
```

## SQLite Specifics

### Pragmas

```python
# Enabled in database.py
PRAGMA foreign_keys = ON
```

### Useful Pragmas

```sql
-- Check integrity
PRAGMA integrity_check;

-- Database info
PRAGMA page_count;
PRAGMA page_size;
PRAGMA schema_version;

-- Performance
PRAGMA cache_size = -32768;  -- 32MB cache
PRAGMA journal_mode = WAL;   -- Write-Ahead Logging
PRAGMA synchronous = NORMAL;
```

### WAL Mode

```python
# Enable WAL for better concurrency
engine = create_engine(
    "sqlite:///./data/catalog.db",
    connect_args={
        "check_same_thread": False,
    },
    execution_options={"sqlite_fast_path": True},
)

with engine.connect() as conn:
    conn.execute(text("PRAGMA journal_mode=WAL"))
```

## Troubleshooting

### Database Locked

```bash
# Check for open connections
lsof data/catalog.db

# Kill processes
fuser -k data/catalog.db
```

### Corrupted Database

```bash
# Check integrity
sqlite3 data/catalog.db "PRAGMA integrity_check;"

# Recover (if possible)
sqlite3 data/catalog.db ".recover" | sqlite3 recovered.db
```

### Disk Full

```bash
# Check space
df -h data/

# Vacuum to reclaim space
sqlite3 data/catalog.db "VACUUM;"
```

## Monitoring

### Connection Pool

```python
# Check pool status
engine.pool.status()
# Returns: (size, checked_in, checked_out, overflow)
```

### Query Logging

```python
# Enable SQL logging
engine = create_engine(DATABASE_URL, echo=True)

# Or specific logger
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

## Security

### File Permissions

```bash
# Restrict database file
chmod 600 data/catalog.db
chown app:app data/catalog.db
```

### SQL Injection Prevention

```python
# Always use ORM or parameterized queries
# GOOD
session.query(Course).filter(Course.course_code == code).first()

# GOOD (raw SQL with params)
conn.execute(text("SELECT * FROM courses WHERE course_code = :code"), {"code": code})

# BAD (string interpolation)
conn.execute(f"SELECT * FROM courses WHERE course_code = '{code}'")
```

## Migration Checklist

When changing schema:

1. [ ] Update `models.py`
2. [ ] Update `schemas.py` if API changes
3. [ ] Update `data/seed.py` for new seed data
4. [ ] Create migration (Alembic for PostgreSQL)
5. [ ] Update tests if needed
6. [ ] Test migration on copy of production data
7. [ ] Deploy with rollback plan