from importlib import import_module

from beanie import init_beanie
from pymongo import AsyncMongoClient

from vibetuner.config import settings
from vibetuner.logging import logger
from vibetuner.models.registry import get_all_models


async def init_models() -> None:
    """Initialize MongoDB connection and register all Beanie models."""

    # Try to import user models to trigger their registration
    try:
        import_module("app.models")
    except ModuleNotFoundError:
        # Silent pass for missing app.models module (expected in some projects)
        pass
    except ImportError as e:
        # Log warning for any import error (including syntax errors, missing dependencies, etc.)
        logger.warning(
            f"Failed to import app.models: {e}. User models will not be registered."
        )

    client: AsyncMongoClient = AsyncMongoClient(
        host=str(settings.mongodb_url),
        compressors=["zstd"],
    )

    await init_beanie(
        database=client[settings.mongo_dbname], document_models=get_all_models()
    )
