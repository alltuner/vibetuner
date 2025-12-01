# ABOUTME: SQLModel/SQLAlchemy async engine setup and session management.
# ABOUTME: Provides database initialization, teardown, and FastAPI dependency injection.

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from vibetuner.config import settings
from vibetuner.logging import logger


# These will be filled lazily if/when database_url is set
engine: Optional[AsyncEngine] = None
async_session: Optional[async_sessionmaker[AsyncSession]] = None


def _ensure_engine() -> None:
    """
    Lazily configure the engine + sessionmaker if database_url is set.

    Safe to call multiple times.
    """
    global engine, async_session

    if settings.database_url is None:
        logger.warning("database_url is not configured. SQLModel engine is disabled.")
        return

    if engine is None:
        engine = create_async_engine(
            str(settings.database_url),
            echo=settings.debug,
        )
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


async def init_sqlmodel() -> None:
    """
    Called from lifespan/startup.
    Initializes the database engine if DB is configured.

    Note: This does NOT create tables. Use `vibetuner db create-schema` CLI command
    for schema creation, or call `create_schema()` directly.
    """
    _ensure_engine()

    if engine is None:
        # Nothing to do, DB not configured
        return

    logger.info("SQLModel engine initialized successfully.")


async def create_schema() -> None:
    """
    Create all tables defined in SQLModel metadata.

    Call this from the CLI command `vibetuner db create-schema` or manually
    during initial setup. This is idempotent - existing tables are not modified.
    """
    _ensure_engine()

    if engine is None:
        raise RuntimeError("database_url is not configured. Cannot create schema.")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("SQLModel schema created successfully.")


async def teardown_sqlmodel() -> None:
    """
    Called from lifespan/shutdown.
    """
    global engine

    if engine is None:
        return

    await engine.dispose()
    engine = None
    logger.info("SQLModel engine disposed.")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency.

    If the DB is not configured, you can:
    - raise a RuntimeError (fail fast), OR
    - raise HTTPException(500), OR
    - return a dummy object in tests.
    """
    if async_session is None:
        # Fail fast – you can customize this to HTTPException if used only in web context
        raise RuntimeError("database_url is not configured. No DB session available.")

    async with async_session() as session:
        yield session
