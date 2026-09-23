"""
Database connection and session management for SQLite with SQLAlchemy.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.scan_db import Base

# Async engine for FastAPI route handlers
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync engine for synchronous tasks / migrations if needed
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    import os
    from urllib.parse import urlparse
    for db_url in [settings.DATABASE_URL, settings.SYNC_DATABASE_URL]:
        if "sqlite" in db_url:
            # Extract file path after sqlite:/// or sqlite+aiosqlite:///
            clean_path = db_url.split(":///")[-1]
            if clean_path and clean_path != ":memory:":
                parent_dir = os.path.dirname(os.path.abspath(clean_path))
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
