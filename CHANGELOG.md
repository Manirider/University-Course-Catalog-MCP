# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-08-15

### Added
- **MCP Server Implementation** with Streamable HTTP transport
- **4 MCP Tools**:
  - `search_courses` - Full-text search across course codes, titles, descriptions
  - `get_prerequisites` - Direct (non-transitive) prerequisite retrieval
  - `lookup_instructor` - Case-insensitive instructor search
  - `get_prerequisite_graph` - Complete transitive dependency graph
- **2 MCP Resources**:
  - `resource://course_descriptions` - All courses with full descriptions
  - `resource://department_directory` - All departments with codes
- **2 MCP Prompts**:
  - `course_comparison_template` - Structured course comparison
  - `course_advisor` - Academic advising prompt
- **FastAPI Integration** with health check endpoint (`GET /health`)
- **SQLite Database** with SQLAlchemy 2.0 ORM
- **Auto-seeding** with 5 departments, 8 instructors, 15 courses, 12 prerequisites
- **Docker Support** with multi-stage build and health checks
- **Comprehensive Test Suite** (57 tests covering database, tools, resources, prompts, MCP integration)

### Database Schema
- `departments` - id, name, code (unique)
- `instructors` - id, name, email, office, department_id (FK)
- `courses` - id, course_code (unique), title, description, credits, instructor_id (FK), department_id (FK)
- `prerequisites` - course_id (FK), prerequisite_id (FK) - composite PK

### Data Integrity
- Foreign key constraints enforced (SQLite PRAGMA foreign_keys=ON)
- Unique constraints on course_code and department code
- Indexes on frequently queried columns
- No self-prerequisites or cycles (validated by NetworkX DAG check)

### Error Handling
- Structured `ErrorResponse` for all tools
- Empty query validation
- Nonexistent entity handling
- Case/whitespace normalization

### Testing
- Database schema validation (10 tests)
- Health endpoint tests (2 tests)
- MCP integration tests (10 tests)
- Tool behavior tests (17 tests)
- Resource content tests (8 tests)
- Prompt template tests (4 tests)
- Total: 57 passing tests

### Documentation
- Professional README with architecture diagrams
- API reference with examples
- MCP protocol usage guide
- Data model documentation
- Seeded data reference
- Troubleshooting guide
- Contributing guidelines

### Infrastructure
- Multi-stage Dockerfile (python:3.12-slim)
- Docker Compose with health checks
- Volume persistence for database
- Environment-based configuration
- .dockerignore and .gitignore optimized

---

## [Unreleased]

### Planned
- [ ] Add pagination to search_courses
- [ ] Implement course_advisor prompt with real catalog data
- [ ] Add OpenAPI/Swagger documentation
- [ ] Support for PostgreSQL in production
- [ ] Authentication/authorization layer
- [ ] Rate limiting
- [ ] Metrics and monitoring (Prometheus)
- [ ] CI/CD pipeline with GitHub Actions