# Architecture

## Overview

Clean architecture with clear separation of concerns across layers.

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                        │
│  Tools  │  Resources  │  Prompts  │  HTTP Transport          │
├─────────────────────────────────────────────────────────────┤
│                      Service Layer                           │
│         CourseService    │    InstructorService             │
├─────────────────────────────────────────────────────────────┤
│                     Repository Layer                         │
│        CourseRepository  │  DepartmentRepository            │
│        InstructorRepository                                   │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer                              │
│        SQLAlchemy Models  │  Database (SQLite)               │
├─────────────────────────────────────────────────────────────┤
│                      Config Layer                            │
│        Pydantic Settings  │  Environment Variables          │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### MCP Layer (`src/university_catalog/mcp/`)

| File | Responsibility |
|------|----------------|
| `server.py` | FastMCP server factory |
| `tools.py` | 4 tool implementations with validation |
| `resources.py` | 2 resource implementations |
| `prompts.py` | 2 prompt template implementations |

**Key Principles:**
- Thin adapters over services
- Input validation via Pydantic schemas
- Structured error responses
- Protocol-specific serialization (JSON for tools)

### Service Layer (`src/university_catalog/services/`)

| File | Responsibility |
|------|----------------|
| `course_service.py` | Search, prerequisites, graph traversal |
| `instructor_service.py` | Instructor lookup |

**Key Principles:**
- Business logic encapsulation
- Data transformation (ORM → Pydantic)
- Transaction management
- No direct database access

### Repository Layer (`src/university_catalog/repositories/`)

| File | Responsibility |
|------|----------------|
| `course_repository.py` | All course/instructor/department queries |

**Key Principles:**
- Data access abstraction
- Query encapsulation
- No business logic
- Session management

### Data Layer (`src/university_catalog/models.py`, `database.py`)

| File | Responsibility |
|------|----------------|
| `models.py` | SQLAlchemy ORM models |
| `database.py` | Engine, session factory, initialization |

**Key Principles:**
- Declarative schema definition
- Relationship mapping
- Connection pooling
- SQLite PRAGMA configuration

### Config Layer (`src/university_catalog/config.py`)

- Pydantic Settings for environment variables
- Type-safe configuration
- Default values

## Dependency Flow

```
MCP Layer → Service Layer → Repository Layer → Data Layer
     ↑                                              ↑
     └────────────────── Config Layer ──────────────┘
```

## Design Patterns

### Repository Pattern
```python
class CourseRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def search_courses(self, query: str, dept_code: str = None):
        # Encapsulated query logic
```

### Service Layer
```python
class CourseService:
    def search_courses(self, query: str, dept_code: str = None):
        with get_db_session() as session:
            repo = CourseRepository(session)
            courses = repo.search_courses(query, dept_code)
            return [SearchCourseResult(...) for c in courses]
```

### Factory Pattern (MCP Server)
```python
def create_mcp_server() -> FastMCP:
    mcp = FastMCP("University Course Catalog")
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    return mcp
```

## Session Management

```python
# database.py
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

- Automatic commit/rollback
- Context manager for safety
- Connection pooling via SQLAlchemy

## Error Handling

| Layer | Strategy |
|-------|----------|
| Data | SQLAlchemy exceptions |
| Repository | Convert to domain exceptions |
| Service | Return structured results or raise |
| MCP | Convert to `ErrorResponse` schema |

## Testing Strategy

| Layer | Test Approach |
|-------|---------------|
| Data | Schema validation, constraint tests |
| Repository | Query logic with test database |
| Service | Business logic with mocked repos |
| MCP | End-to-end protocol tests |

## Extensibility

### Adding a Tool
1. Add schema in `schemas.py`
2. Add repository method
3. Add service method
4. Register in `tools.py`
5. Add tests

### Adding a Resource
1. Add repository method
2. Add service formatter
3. Register in `resources.py`
4. Add tests

### Adding a Prompt
1. Implement in `prompts.py`
2. Register in `prompts.py`
3. Add tests

## Performance Considerations

| Concern | Solution |
|---------|----------|
| N+1 queries | Eager loading (`joinedload`, `selectinload`) |
| Graph traversal | NetworkX for complex operations |
| Connection pooling | SQLAlchemy pool (default) |
| Deterministic ordering | Explicit `ORDER BY` clauses |

## Security

- No raw SQL (SQLAlchemy ORM)
- Parameterized queries
- Input validation (Pydantic)
- No secrets in code
- Environment-based config