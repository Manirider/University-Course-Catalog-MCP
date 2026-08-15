# Contributing Guide

Thank you for your interest in contributing to the University Course Catalog MCP Server! This guide will help you get started.

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to the maintainers.

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- Docker (optional, for containerized development)

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/university-course-catalog-mcp.git
cd university-course-catalog-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

Follow the project structure:

```
src/university_catalog/
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic schemas (MCP contracts)
├── repositories/      # Data access layer
├── services/          # Business logic
├── mcp/              # MCP tools/resources/prompts
└── api/              # REST endpoints
```

### 3. Write Tests

Add tests in `tests/` following existing patterns:

```bash
# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tools.py -v
```

### 4. Code Quality

```bash
# Format code
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### 5. Commit Changes

Use conventional commits:

```bash
git add .
git commit -m "feat: add course search by credits filter"
# or
git commit -m "fix: handle empty prerequisite graph for CS101"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Open a Pull Request against `main`.

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass (`pytest -q`)
- [ ] Code formatted (`ruff format`)
- [ ] No lint errors (`ruff check`)
- [ ] Type checking passes (`mypy src/`)
- [ ] New functionality has tests
- [ ] Documentation updated if needed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Follows code style
- [ ] Self-documenting code
- [ ] No console.log/print statements
- [ ] No commented-out code
```

## Architecture Guidelines

### Layer Separation

| Layer | Responsibility | Example |
|-------|----------------|---------|
| Models | Database schema | `models.py` |
| Schemas | API contracts | `schemas.py` |
| Repositories | Data access | `repositories/course_repository.py` |
| Services | Business logic | `services/course_service.py` |
| MCP | Protocol handling | `mcp/tools.py` |

### Adding a New Tool

1. **Schema** - Add input/output schemas in `schemas.py`
2. **Repository** - Add data access method in `repositories/`
3. **Service** - Implement business logic in `services/`
4. **MCP Tool** - Register in `mcp/tools.py`
5. **Tests** - Add tests in `tests/test_tools.py` and `tests/test_mcp_integration.py`

### Adding a New Resource

1. **Repository** - Add data access method
2. **Service** - Implement formatting logic
3. **MCP Resource** - Register in `mcp/resources.py`
4. **Tests** - Add tests in `tests/test_resources.py`

### Adding a New Prompt

1. **MCP Prompt** - Implement in `mcp/prompts.py`
2. **Tests** - Add tests in `tests/test_prompts.py`

## Database Changes

For schema modifications:

```bash
# 1. Update models.py
# 2. Delete database (SQLite doesn't support migrations easily)
rm data/catalog.db

# 3. Update seed.py if needed
# 4. Restart server (auto-seeds)
python -m uvicorn university_catalog.main:app --reload
```

## Testing Philosophy

### Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Database | `test_database.py` | Schema, constraints, integrity |
| Tools | `test_tools.py` | Business logic behavior |
| Resources | `test_resources.py` | Content completeness |
| Prompts | `test_prompts.py` | Template correctness |
| Health | `test_health.py` | HTTP endpoints |
| MCP Integration | `test_mcp_integration.py` | End-to-end protocol |

### Writing Good Tests

```python
# Good: Specific, isolated, descriptive
def test_search_courses_returns_empty_for_unknown_department():
    service = CourseService()
    results = service.search_courses("programming", department_code="NONEXISTENT")
    assert results == []

# Good: Test edge cases
def test_search_courses_handles_whitespace():
    service = CourseService()
    results = service.search_courses("  programming  ")
    assert len(results) > 0

# Good: Test error responses
def test_get_prerequisites_returns_error_for_unknown_course():
    result = await mcp.call_tool("get_prerequisites", {"course_code": "UNKNOWN"})
    assert "error" in result[0].text
```

## Code Style

### Python Style

- Follow PEP 8 (enforced by Ruff)
- Type hints required for all public functions
- Docstrings for all public classes/functions
- Max line length: 100 characters

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `CourseService` |
| Functions | snake_case | `search_courses` |
| Variables | snake_case | `course_code` |
| Constants | UPPER_SNAKE_CASE | `MAX_CREDITS` |
| Private | _leading_underscore | `_internal_method` |

### Imports

```python
# Standard library
import json
from typing import List, Optional

# Third-party
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Local
from university_catalog.models import Course
from university_catalog.schemas import SearchCourseResult
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def search_courses(self, query: str, department_code: Optional[str] = None) -> List[SearchCourseResult]:
    """Search for courses by keyword with optional department filtering.

    Args:
        query: Search term for course code, title, or description.
        department_code: Optional department code to filter results.

    Returns:
        List of matching courses with code, title, and credits.

    Raises:
        ValueError: If query is empty.
    """
```

### README Updates

Update `README.md` when:
- Adding new tools/resources/prompts
- Changing API behavior
- Adding configuration options
- Updating architecture

## Release Process

Maintainers only:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v1.1.0`
4. Push tag: `git push origin v1.1.0`
5. GitHub Actions builds and publishes

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/university-course-catalog-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/university-course-catalog-mcp/discussions)
- **MCP Spec**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)

## Recognition

Contributors will be added to the README's acknowledgments section.

Thank you for contributing! 🎓