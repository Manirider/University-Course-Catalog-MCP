# Testing Guide

## Overview

Comprehensive test suite with 57 tests covering all layers.

## Test Structure

```
tests/
├── test_database.py      # Schema, constraints, integrity (10 tests)
├── test_health.py        # HTTP endpoints (2 tests)
├── test_mcp_integration.py  # End-to-end MCP (10 tests)
├── test_prompts.py       # Prompt templates (4 tests)
├── test_resources.py     # Resource content (8 tests)
├── test_tools.py         # Tool behavior (17 tests)
└── conftest.py           # Shared fixtures (if needed)
```

## Running Tests

### All Tests

```bash
# Quick
pytest -q

# Verbose
pytest -v

# With coverage
pytest --cov=university_catalog --cov-report=term-missing --cov-report=html
```

### Specific Modules

```bash
pytest tests/test_tools.py -v
pytest tests/test_mcp_integration.py -v
pytest tests/test_database.py -v
```

### Parallel Execution

```bash
pytest -n auto  # Requires pytest-xdist
```

## Test Categories

### Database Tests (`test_database.py`)

```python
# Schema validation
def test_tables_exist(setup_database):
    assert "departments" in tables
    assert "courses" in tables

# Constraints
def test_unique_course_codes(setup_database):
    codes = session.query(Course.course_code).all()
    assert len(codes) == len(set(codes))

# Referential integrity
def test_foreign_key_integrity(setup_database):
    for course in courses:
        assert session.query(Instructor).filter(Instructor.id == course.instructor_id).first()

# No cycles
def test_no_prerequisite_cycles(setup_database):
    G = nx.DiGraph()
    for p in prereqs:
        G.add_edge(p.prerequisite_id, p.course_id)
    assert nx.is_directed_acyclic_graph(G)
```

### Tool Tests (`test_tools.py`)

```python
class TestSearchCourses:
    def test_search_by_keyword(self):
        service = CourseService()
        results = service.search_courses("programming")
        assert len(results) > 0
    
    def test_search_case_insensitive(self):
        results_lower = service.search_courses("programming")
        results_upper = service.search_courses("PROGRAMMING")
        assert len(results_lower) == len(results_upper)
    
    def test_department_filter(self):
        results = service.search_courses("programming", department_code="CS")
        assert all(r.course_code.startswith("CS") for r in results)
    
    def test_deterministic_ordering(self):
        results1 = service.search_courses("CS")
        results2 = service.search_courses("CS")
        assert [r.course_code for r in results1] == [r.course_code for r in results2]

class TestGetPrerequisites:
    def test_course_with_prerequisites(self):
        result = service.get_prerequisites("CS301")
        assert len(result.prerequisites) == 1
        assert result.prerequisites[0].course_code == "CS102"
    
    def test_course_without_prerequisites(self):
        result = service.get_prerequisites("CS101")
        assert result.prerequisites == []
    
    def test_unknown_course(self):
        result = service.get_prerequisites("INVALID")
        assert result.course_code == "INVALID"
        assert result.prerequisites == []

class TestPrerequisiteGraph:
    def test_multi_level_chain(self):
        result = service.get_prerequisite_graph("CS301")
        node_ids = {n.id for n in result.nodes}
        assert node_ids == {"CS101", "CS102", "CS301"}
        edges = {(e.source, e.target) for e in result.edges}
        assert edges == {("CS101", "CS102"), ("CS102", "CS301")}
```

### MCP Integration Tests (`test_mcp_integration.py`)

```python
@pytest.mark.asyncio
async def test_mcp_tools_registered():
    tools = await mcp_server.list_tools()
    tool_names = {tool.name for tool in tools}
    assert tool_names == {"search_courses", "get_prerequisites", "lookup_instructor", "get_prerequisite_graph"}

@pytest.mark.asyncio
async def test_mcp_tool_search_courses():
    result = await mcp_server.call_tool("search_courses", {"query": "programming"})
    courses = json.loads(result[0].text)
    assert isinstance(courses, list)
    assert all("course_code" in c for c in courses)

@pytest.mark.asyncio
async def test_mcp_tool_get_prerequisite_graph():
    result = await mcp_server.call_tool("get_prerequisite_graph", {"course_code": "CS301"})
    data = json.loads(result[0].text)
    assert data["nodes"] == [{"id": "CS101"}, {"id": "CS102"}, {"id": "CS301"}]
```

## Fixtures

### Database Fixture (`conftest.py`)

```python
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()
    seed_database()
    yield
```

### Async Client Fixture

```python
@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
```

## Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| Database | 100% | 100% |
| Services | 95% | 95% |
| Repositories | 90% | 90% |
| MCP Layer | 95% | 95% |
| API | 100% | 100% |

## Writing Good Tests

### Principles

1. **Isolated** — Each test independent
2. **Descriptive** — Name explains what it tests
3. **Deterministic** — Same result every run
4. **Fast** — Unit tests < 100ms
5. **Maintainable** — Easy to update

### Patterns

```python
# Arrange-Act-Assert
def test_search_returns_cs_courses():
    # Arrange
    service = CourseService()
    
    # Act
    results = service.search_courses("", department_code="CS")
    
    # Assert
    assert all(r.course_code.startswith("CS") for r in results)

# Parametrized tests
@pytest.mark.parametrize("query,expected_count", [
    ("programming", 3),
    ("data", 6),
    ("nonexistent", 0),
])
def test_search_result_counts(query, expected_count):
    service = CourseService()
    results = service.search_courses(query)
    assert len(results) == expected_count

# Edge cases
def test_empty_query_returns_error():
    result = await mcp_server.call_tool("search_courses", {"query": ""})
    assert "error" in json.loads(result[0].text)
```

## Test Data

### Using Seeded Data

```python
# Tests rely on seeded data
# CS101 → CS102 → CS301 chain exists
# 5 departments, 8 instructors, 15 courses, 12 prerequisites
```

### Creating Test Data (if needed)

```python
@pytest.fixture
def test_course(db_session):
    course = Course(
        course_code="TEST101",
        title="Test Course",
        description="Test description",
        credits=3,
        instructor_id=1,
        department_id=1,
    )
    db_session.add(course)
    db_session.commit()
    return course
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/ci.yml
- name: Run Tests
  run: pytest --cov=university_catalog --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v4
```

### Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest -q
        language: system
        types: [python]
```

## Debugging Tests

### Verbose Output

```bash
pytest tests/test_tools.py::TestSearchCourses::test_search_by_keyword -v -s
```

### Debug on Failure

```bash
pytest tests/test_tools.py -x --pdb
```

### Print Statements

```python
def test_debug(self):
    result = service.search_courses("test")
    print(f"Results: {result}")  # Visible with -s flag
```

## Performance Testing

```python
import time

def test_search_performance():
    service = CourseService()
    start = time.perf_counter()
    for _ in range(100):
        service.search_courses("programming")
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0  # Should complete in under 1 second
```

## Test Database

### In-Memory for Speed

```python
# conftest.py
@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine
```

### Transaction Rollback

```python
@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```