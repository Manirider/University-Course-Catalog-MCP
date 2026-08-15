from fastapi import APIRouter
from sqlalchemy import text

from university_catalog.database import get_engine
from university_catalog.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    db_status = "disconnected"
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except (OSError, ImportError, RuntimeError):
        db_status = "disconnected"

    return HealthResponse(status="healthy", database=db_status)
