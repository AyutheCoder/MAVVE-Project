"""
MAVVE — Multi-Agent Vernacular Validation Ecosystem
Main FastAPI application entry point.
"""

import sys
print("=== MAVVE APP IMPORT STARTING ===", flush=True)
print("SYS.ARGV:", sys.argv, flush=True)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from config import settings
from api.health import router as health_router
from api.webhooks import router as webhooks_router
from api.orders import router as orders_router
from api.dashboard import router as dashboard_router
from api.simulator import router as simulator_router
from api.demo import router as demo_router


# ── Structured Logging ───────────────────────────────────
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        structlog.get_config()["wrapper_class"]._default_level
        if hasattr(structlog.get_config().get("wrapper_class", object), "_default_level")
        else 0
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


# ── Application Lifespan ─────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("=== LIFESPAN STARTING ===", flush=True)
    logger.info(
        "mavve_startup",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        llm_provider=settings.LLM_PROVIDER,
        rto_threshold=settings.RTO_RISK_THRESHOLD,
    )

    # Auto-create tables in development mode
    if settings.APP_ENV == "development":
        try:
            print("=== CREATING TABLES ===", flush=True)
            from db.database import create_all_tables
            await create_all_tables()
            print("=== TABLES CREATED ===", flush=True)
            logger.info("database_tables_created")
        except Exception as e:
            print(f"=== TABLE ERROR: {e} ===", flush=True)
            logger.warning("database_tables_creation_skipped", error=str(e))

    print("=== LIFESPAN READY ===", flush=True)
    yield
    print("=== LIFESPAN SHUTDOWN ===", flush=True)
    logger.info("mavve_shutdown")


# ── FastAPI App ──────────────────────────────────────────
app = FastAPI(
    title="MAVVE API",
    description=(
        "Multi-Agent Vernacular Validation Ecosystem — "
        "Agentic AI for reducing RTO in Bharat e-commerce"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────
app.include_router(health_router, tags=["Health"])
app.include_router(orders_router, prefix="/api/orders", tags=["Orders"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(simulator_router, prefix="/api/simulator", tags=["Simulator"])
app.include_router(demo_router, prefix="/api/demo", tags=["Demo"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])


# ── Root Endpoint ────────────────────────────────────────
@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "Multi-Agent Vernacular Validation Ecosystem",
        "docs": "/docs",
        "health": "/health",
    }
