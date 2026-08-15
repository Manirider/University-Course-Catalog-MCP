# Adding Features

## Overview

Guide for extending the server with new tools, resources, and prompts.

## Adding a New Tool

### 1. Define Schema (`schemas.py`)

```python
class NewToolInput(BaseModel):
    param1: Annotated[str, Field(description="Description")]
    param2: Annotated[Optional[int], Field(default=None, description="Optional param")]

class NewToolResult(BaseModel):
    field1: Annotated[str, Field(description="Result field")]
    field2: Annotated[List[str], Field(description="List result")]
```

### 2. Add Repository Method (`repositories/course_repository.py`)

```python
def new_operation(self, param1: str, param2: int = None) -> List[Course]:
    stmt = self.session.query(Course).filter(...)
    if param2:
        stmt = stmt.filter(...)
    return stmt.all()
```

### 3. Add Service Method (`services/course_service.py`)

```python
def new_operation(self, param1: str, param2: int = None) -> List[NewToolResult]:
    with get_db_session() as session:
        repo = CourseRepository(session)
        courses = repo.new_operation(param1, param2)
        return [NewToolResult(field1=c.course_code, field2=[...]) for c in courses]
```

### 4. Register MCP Tool (`mcp/tools.py`)

```python
@mcp.tool(
    name="new_tool",
    description="Description for LLM",
)
def new_tool(param1: str, param2: int | None = None) -> Union[NewToolResult, ErrorResponse]:
    """Docstring for IDE support."""
    if not param1:
        return ErrorResponse(error="param1 is required")
    return course_service.new_operation(param1, param2)
```

### 5. Add Tests (`tests/test_tools.py`, `tests/test_mcp_integration.py`)

```python
class TestNewTool:
    def test_new_tool_basic(self):
        service = CourseService()
        results = service.new_operation("test")
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_mcp_new_tool(self):
        result = await mcp_server.call_tool("new_tool", {"param1": "test"})
        data = json.loads(result[0].text)
        assert "field1" in data
```

---

## Adding a New Resource

### 1. Add Repository Method

```python
def get_resource_data(self) -> List[SomeModel]:
    return self.session.query(SomeModel).all()
```

### 2. Add Service Formatter

```python
def format_resource(self) -> str:
    with get_db_session() as session:
        repo = SomeRepository(session)
        items = repo.get_resource_data()
        return "\n".join(f"{item.field}: {item.value}" for item in items)
```

### 3. Register MCP Resource (`mcp/resources.py`)

```python
def my_resource() -> str:
    return course_service.format_resource()

def register_resources(mcp: FastMCP):
    mcp.resource(
        uri="resource://my_resource",
        name="my_resource",
        description="Description",
        mime_type="text/plain",
    )(my_resource)
```

### 4. Add Tests

```python
def test_my_resource(self):
    result = my_resource()
    assert "expected_content" in result
```

---

## Adding a New Prompt

### 1. Implement Prompt (`mcp/prompts.py`)

```python
def my_prompt_template(arg1: str, arg2: str) -> str:
    """Description for LLM."""
    return f"""Template with {{arg1}} and {{arg2}}.
    
    Provide analysis based on these parameters."""
```

### 2. Register MCP Prompt

```python
def register_prompts(mcp: FastMCP):
    mcp.prompt(
        name="my_prompt",
        description="Description for discovery",
    )(my_prompt_template)
```

### 3. Add Tests

```python
def test_my_prompt(self):
    result = my_prompt_template("value1", "value2")
    assert "{{arg1}}" in result
    assert "value1" not in result  # Template, not rendered
```

---

## Adding Database Fields

### 1. Update Model (`models.py`)

```python
class Course(Base):
    # ... existing fields
    new_field = Column(String(100), nullable=True)
```

### 2. Update Seed (`data/seed.py`)

```python
course = Course(
    # ... existing fields
    new_field="default_value",
)
```

### 3. Migrate Database

```bash
# Development: Drop and reseed
rm data/catalog.db
python -m uvicorn university_catalog.main:app

# Production: Use Alembic
alembic revision --autogenerate -m "Add new_field to courses"
alembic upgrade head
```

### 4. Update Schemas & Services

Update corresponding Pydantic schemas and service methods to include new field.

---

## Adding a New Department/Course (Data Only)

Edit `data/seed.py`:

```python
departments_data = [
    # ... existing
    {"name": "New Department", "code": "NEW"},
]

instructors_data = [
    # ... existing
    {"name": "Dr. New Prof", "email": "new@university.edu", "office": "NEW-101", "department_code": "NEW"},
]

courses_data = [
    # ... existing
    {"course_code": "NEW101", "title": "Intro to New", "description": "...", "credits": 3, "instructor": "Dr. New Prof", "department_code": "NEW"},
]

prerequisites_data = [
    # ... existing
    ("NEW201", "NEW101"),
]
```

Then reseed:
```bash
rm data/catalog.db
python -m uvicorn university_catalog.main:app
```

---

## Best Practices

| Practice | Description |
|----------|-------------|
| **Schema first** | Define Pydantic models before implementation |
| **Thin MCP layer** | Delegate to services |
| **Service = business logic** | No DB access in MCP layer |
| **Repository = queries** | No business logic in repositories |
| **Test at each layer** | Unit + integration tests |
| **Error responses** | Use `ErrorResponse` schema consistently |
| **Validation** | Input validation in MCP layer, business rules in service |
| **Documentation** | Update relevant docs |