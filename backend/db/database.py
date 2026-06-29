"""
Database configuration with async SQLAlchemy engine and session factory.
Provides the declarative Base, engine, session maker, and table-management utilities.
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text

from config import settings


# ── Async Engine ─────────────────────────────────────────
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ── Session Factory ──────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative Base ─────────────────────────────────────
class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""
    pass


# ── FastAPI Dependency ───────────────────────────────────
async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields a database session.
    Commits on success, rolls back on error, always closes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Table Management ─────────────────────────────────────
async def create_all_tables() -> None:
    """
    Create all tables defined by models that inherit from Base.
    Used during development and testing; production uses Alembic migrations.
    """
    # Import models to register them with Base.metadata
    import models  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables() -> None:
    """Drop all tables. USE WITH EXTREME CAUTION — data loss is irreversible."""
    import models  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def check_connection() -> bool:
    """Return True if the database is reachable."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
