from importlib import import_module
from typing import Optional

from beanie import init_beanie
from deprecated import deprecated
from pymongo import AsyncMongoClient

from vibetuner.config import settings
from vibetuner.logging import logger
from vibetuner.models.registry import get_all_models


# Global singleton, created lazily
mongo_client: Optional[AsyncMongoClient] = None


def _ensure_client() -> None:
    """
    Lazily create the global MongoDB client if mongodb_url is configured.
    Safe to call many times.
    """
    global mongo_client

    if settings.mongodb_url is None:
        logger.warning("MongoDB URL is not configured. Mongo engine disabled.")
        return

    if mongo_client is None:
        mongo_client = AsyncMongoClient(
            host=str(settings.mongodb_url),
            compressors=["zstd"],
        )
        logger.debug("MongoDB client created.")


async def init_mongodb() -> None:
    """Initialize MongoDB and register Beanie models."""
    _ensure_client()

    if mongo_client is None:
        # Nothing to do; URL missing
        return

    # Import user models so they register themselves
    try:
        import_module("app.models")
    except ModuleNotFoundError:
        logger.debug("app.models not found; skipping user model import.")
    except ImportError as e:
        logger.warning(f"Failed to import app.models: {e}. User models may be missing.")

    await init_beanie(
        database=mongo_client[settings.mongo_dbname],
        document_models=get_all_models(),
    )
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
