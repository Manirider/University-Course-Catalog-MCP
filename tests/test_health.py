import pytest
from httpx import AsyncClient

from university_catalog.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "database" in data
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "University Course Catalog MCP Server"
    assert data["mcp_endpoint"] == "/mcp"
    assert data["health_endpoint"] == "/health"
