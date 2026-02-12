# ABOUTME: SQLModel/SQLAlchemy async engine setup and session management.
# ABOUTME: Provides database initialization, teardown, and FastAPI dependency injection.

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

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
        logger.debug("DATABASE_URL not configured — skipping SQLModel engine")
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


def get_all_sql_models() -> list[type[SQLModel]]:
    """Get all registered SQL models from tune.py."""
    from vibetuner.loader import load_app_config

    return list(load_app_config().sql_models)


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

    sql_models = get_all_sql_models()
    if sql_models:
        logger.debug(
            "Registered {} SQL model(s): {}",
            len(sql_models),
            ", ".join(m.__name__ for m in sql_models),
        )

    logger.info("SQLModel engine initialized successfully.")

    if settings.debug:
        await create_schema()
        logger.info("SQLModel tables auto-created (DEBUG mode)")


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
    _ensure_engine()
    if async_session is None:
        raise RuntimeError("database_url is not configured. No DB session available.")

    async with async_session() as session:
        yield session
