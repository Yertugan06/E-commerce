import time
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine
from app.core.metrics import db_available

logger = logging.getLogger(__name__)


async def health_endpoint(request: Request) -> JSONResponse:
    db_status = "unknown"
    db_error = None
    db_latency = None

    if settings.SLI_ENABLED:
        try:
            start = time.monotonic()
            async with AsyncSession(engine) as session:
                await session.execute(text("SELECT 1"))
            db_latency = time.monotonic() - start
            db_status = "up"
            db_available.set(1)
        except Exception as exc:
            db_available.set(0)
            db_status = "down"
            db_error = str(exc)
            logger.warning("Database health check failed: %s", exc)

    return JSONResponse(
        status_code=200 if db_status == "up" else 503,
        content={
            "status": "ok" if db_status == "up" else "degraded",
            "database": {
                "status": db_status,
                "latency_ms": round(db_latency * 1000, 2) if db_latency is not None else None,
                "error": db_error,
            },
            "version": "0.1.0",
        },
    )
