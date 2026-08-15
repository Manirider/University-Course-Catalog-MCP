# Root Endpoint

## Overview

The root endpoint provides basic server information and discoverability for the MCP endpoint.

## Endpoint

```
GET /
```

## Response

### Success (200 OK)

```json
{
  "name": "University Course Catalog MCP Server",
  "version": "1.0.0",
  "mcp_endpoint": "/mcp",
  "health_endpoint": "/health"
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Server display name |
| `version` | string | Semantic version |
| `mcp_endpoint` | string | MCP protocol endpoint path |
| `health_endpoint` | string | Health check endpoint path |

## Usage Examples

### cURL

```bash
curl http://localhost:8080/
```

### Browser

Navigate to `http://localhost:8080/` for JSON response.

### Programmatic Discovery

```python
import httpx

async def discover_server(base_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url)
        info = response.json()
        return {
            "mcp_url": f"{base_url}{info['mcp_endpoint']}",
            "health_url": f"{base_url}{info['health_endpoint']}"
        }
```

## Purpose

- **Service discovery** — Clients can find MCP endpoint automatically
- **Version identification** — API version tracking
- **Health check location** — Standardized health endpoint path
- **Human readable** — Server identification

## Implementation

```python
# src/university_catalog/main.py
@app.get("/")
async def root():
    return {
        "name": "University Course Catalog MCP Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health",
    }
```

## Related

- [Health Check](./health.md) — Detailed health endpoint
- [MCP Transport](../mcp/transport.md) — Protocol endpoint details
- [Quick Start](../getting-started/quickstart.md) — Getting started guide