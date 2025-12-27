"""
Database Connection
===================

SQLAlchemy engine and session configuration.
Supports both sync and async database operations.
"""

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from ..models.base import Base
from ..utils.logger import get_logger

logger = get_logger(__name__)


def get_sync_url() -> str:
    """Get synchronous database URL."""
    url = settings.database.database_url
    # Ensure we're using the sync driver
    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql")
    return url


def get_async_url() -> str:
    """Get async database URL."""
    url = settings.database.database_url
    # Convert to async driver if needed
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://")
    return url


# Create sync engine
engine = create_engine(
    get_sync_url(),
    pool_size=settings.database.db_pool_size,
    max_overflow=settings.database.db_max_overflow,
    echo=settings.database.db_echo,
    pool_pre_ping=True,  # Enable connection health checks
)

# Create async engine
async_engine = create_async_engine(
    get_async_url(),
    pool_size=settings.database.db_pool_size,
    max_overflow=settings.database.db_max_overflow,
    echo=settings.database.db_echo,
    pool_pre_ping=True,
)

# Session factories
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get a synchronous database session.
    
    Usage:
        with get_db() as db:
            users = db.query(User).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    Usage:
        async with get_async_db() as db:
            result = await db.execute(select(User))
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for async database sessions.
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    Should be called on application startup in development/testing.
    For production, use Alembic migrations.
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


async def init_async_db() -> None:
    """
    Async version of database initialization.
    """
    logger.info("Initializing database tables (async)...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def close_db() -> None:
    """
    Close database connections.
    
    Should be called on application shutdown.
    """
    logger.info("Closing database connections...")
    await async_engine.dispose()
    engine.dispose()
    logger.info("Database connections closed")
