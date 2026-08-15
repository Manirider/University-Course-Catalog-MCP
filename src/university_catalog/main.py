import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.routing import Mount

from university_catalog.api import health_router
from university_catalog.database import init_db
from university_catalog.mcp import mcp_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up University Course Catalog MCP Server...")
    init_db()
    from university_catalog.seed import seed_database

    seed_database()
    logger.info("Database initialized and seeded")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="University Course Catalog MCP Server",
    description="MCP Server for university course catalog with tools, resources, and prompts",
    version="1.0.0",
    lifespan=lifespan,
    routes=[
        Mount("/mcp", app=mcp_server.sse_app()),
    ],
)

app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "name": "University Course Catalog MCP Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health",
    }
