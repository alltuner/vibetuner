# ABOUTME: MongoDB client and Beanie ODM initialization.
# ABOUTME: Manages connection lifecycle and model registration.
from typing import Optional

from beanie import init_beanie
from deprecated import deprecated
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure

from vibetuner.config import settings
from vibetuner.loader import load_app_config
from vibetuner.logging import logger
from vibetuner.models import __all__ as core_models


# Global singleton, created lazily
mongo_client: Optional[AsyncMongoClient] = None


def _ensure_client() -> None:
    """Lazily create the global MongoDB client if mongodb_url is configured."""
    global mongo_client

    if settings.mongodb_url is None:
        from vibetuner.services.errors import mongodb_not_configured

        mongodb_not_configured()
        return

    if mongo_client is None:
        mongo_client = AsyncMongoClient(
            host=str(settings.mongodb_url),
            compressors=["zstd"],
        )
        logger.debug("MongoDB client created.")


def get_all_models() -> list[type]:
    """Get all models: core vibetuner models + user models from tune.py."""
    app_config = load_app_config()
    return list(core_models) + list(app_config.models)


async def init_mongodb() -> None:
    """Initialize MongoDB and register Beanie models.

    Skips if mongodb_url is not configured. Warns if user models are registered
    without a database URL, since those models will fail at runtime.
    """
    if settings.mongodb_url is None:
        app_config = load_app_config()
        if app_config.models:
            logger.warning(
                "MONGODB_URL is not set but {} user model(s) are registered. "
                "MongoDB-dependent features will fail. "
                "Check that .env is at the project root or set MONGODB_URL explicitly.",
                len(app_config.models),
            )
        else:
            logger.debug(
                "MongoDB not configured (no MONGODB_URL) — skipping initialization"
            )
        return

    _ensure_client()

    if mongo_client is None:
        return

    all_models = get_all_models()
    logger.debug(f"Initializing Beanie with {len(all_models)} models")

    try:
        await init_beanie(
            database=mongo_client[settings.mongo_dbname],
            document_models=all_models,
        )
    except ConnectionFailure as exc:
        url = settings.mongodb_url
        logger.error(
            "Failed to connect to MongoDB at {}: {}",
            f"{url.host}:{url.port}" if url else "unknown",
            exc,
        )
        raise

    logger.info("MongoDB + Beanie initialized successfully.")


async def teardown_mongodb() -> None:
    """Dispose the MongoDB client."""
    global mongo_client

    if mongo_client is not None:
        await mongo_client.close()
        mongo_client = None
        logger.info("MongoDB client closed.")
    else:
        logger.debug("MongoDB client was never initialized; nothing to tear down.")


@deprecated(reason="Use init_mongodb() instead")
async def init_models() -> None:
    await init_mongodb()
