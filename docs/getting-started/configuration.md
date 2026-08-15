# Configuration

## Environment Variables

All configuration is managed via environment variables with sensible defaults.

### `.env.example`

```bash
DATABASE_URL=sqlite:///./data/catalog.db
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
```

### Variable Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | `sqlite:///./data/catalog.db` | SQLAlchemy database URL |
| `HOST` | string | `0.0.0.0` | Server bind address |
| `PORT` | integer | `8080` | Server port |
| `LOG_LEVEL` | string | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |

## Database Configuration

### SQLite (Default)

```bash
DATABASE_URL=sqlite:///./data/catalog.db
```

- File-based, zero-configuration
- Automatic schema creation on startup
- Data persists in `./data/catalog.db`
- Suitable for development and small deployments

### PostgreSQL (Production)

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Requires:
- `psycopg2-binary` in requirements.txt
- Database created beforehand
- Run migrations manually (Alembic recommended)

### In-Memory (Testing)

```bash
DATABASE_URL=sqlite:///:memory:
```

- Ephemeral, fast
- No persistence
- Ideal for CI/testing

## Logging Configuration

### Log Levels

| Level | Use Case |
|-------|----------|
| `DEBUG` | Development, troubleshooting |
| `INFO` | Production (default) |
| `WARNING` | Reduced verbosity |
| `ERROR` | Errors only |

### Structured Logging

Configure JSON logging for production:

```python
# In main.py or logging config
import logging
import json_logging

json_logging.init_fastapi(enable_json=True)
json_logging.init_request_instrument(app)
```

## MCP Configuration

### Transport

Currently supports **Streamable HTTP** only:

```python
# main.py
routes=[
    Mount("/mcp", app=mcp_server.sse_app()),
]
```

### Endpoint Path

Change MCP endpoint path:

```python
routes=[
    Mount("/api/mcp", app=mcp_server.sse_app()),
]
```

Then update clients to use `http://host:port/api/mcp`

## Security Configuration

### CORS

Add CORS middleware for browser clients:

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

Add rate limiting (requires `slowapi`):

```python
# main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    ...
```

## Feature Flags

Toggle features via environment:

```bash
# Enable/disable specific tools
ENABLE_SEARCH_COURSES=true
ENABLE_GET_PREREQUISITES=true
ENABLE_LOOKUP_INSTRUCTOR=true
ENABLE_PREREQUISITE_GRAPH=true

# Enable/disable resources
ENABLE_COURSE_DESCRIPTIONS=true
ENABLE_DEPARTMENT_DIRECTORY=true

# Enable/disable prompts
ENABLE_COURSE_COMPARISON=true
ENABLE_COURSE_ADVISOR=true
```

## Configuration Validation

Settings are validated using Pydantic Settings:

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/catalog.db"
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

Access in code:

```python
from university_catalog.config import get_settings

settings = get_settings()
print(settings.database_url)
```

## Configuration Precedence

1. **Environment variables** (highest priority)
2. **`.env` file**
3. **Default values** (lowest priority)

```bash
# This overrides .env
DATABASE_URL=postgresql://... python -m uvicorn university_catalog.main:app
```