from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..models import MODELS
from . import project_settings, settings


# Include here any custom things that need to be done after model definitions
# for instance, model rebuilds for documents that contain links


async def init_models() -> None:
    """Initialize MongoDB connection and register all Beanie models."""

    mongo_db: AsyncIOMotorDatabase = AsyncIOMotorClient(
        host=str(project_settings.mongodb_url),
        compressors=["zstd"],
    )[settings.mongo_dbname]

    await init_beanie(database=mongo_db, document_models=MODELS)
