"""
Health check endpoints for MAVVE.
Provides system health status including database and Redis connectivity.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import structlog

from config import settings

router = APIRouter()
logger = structlog.get_logger()

# Track startup time
_startup_time = datetime.now(timezone.utc)


@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns system status, uptime, and component connectivity.
    """
    now = datetime.now(timezone.utc)
    uptime_seconds = (now - _startup_time).total_seconds()

    health = {
        "status": "healthy",
        "timestamp": now.isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "components": {
            "api": {"status": "healthy"},
            "database": {"status": "unchecked"},
            "redis": {"status": "unchecked"},
            "llm": {
                "status": "configured" if (
                    settings.GOOGLE_API_KEY or settings.OPENAI_API_KEY
                ) else "not_configured",
                "provider": settings.LLM_PROVIDER,
            },
            "whatsapp": {
                "status": "configured" if settings.WHATSAPP_API_TOKEN else "not_configured",
            },
            "bhashini": {
                "status": "mock_mode" if settings.BHASHINI_MOCK_MODE else (
                    "configured" if settings.BHASHINI_API_KEY else "not_configured"
                ),
            },
        },
    }

    # Check database connectivity
    try:
        from db.database import async_engine
        from sqlalchemy import text

        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health["components"]["database"]["status"] = "healthy"
    except Exception as e:
        health["components"]["database"]["status"] = "unhealthy"
        health["components"]["database"]["error"] = str(e)
        logger.warning("health_check_db_failed", error=str(e))

    # Check Redis connectivity
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        health["components"]["redis"]["status"] = "healthy"
    except Exception as e:
        health["components"]["redis"]["status"] = "unhealthy"
        health["components"]["redis"]["error"] = str(e)
        logger.warning("health_check_redis_failed", error=str(e))

    # Determine overall status
    component_statuses = [
        c.get("status") for c in health["components"].values()
    ]
    if "unhealthy" in component_statuses:
        health["status"] = "degraded"

    return health


@router.get("/health/ping")
async def ping():
    """Simple liveness probe."""
    return {"ping": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}
