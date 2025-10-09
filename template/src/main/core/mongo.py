from beanie import init_beanie
from pymongo import AsyncMongoClient

from ..models import MODELS
from .config import project_settings, settings


# Include here any custom things that need to be done after model definitions
# for instance, model rebuilds for documents that contain links


async def init_models() -> None:
    """Initialize MongoDB connection and register all Beanie models."""

    client: AsyncMongoClient = AsyncMongoClient(
        host=str(project_settings.mongodb_url),
        compressors=["zstd"],
    )

    await init_beanie(database=client[settings.mongo_dbname], document_models=MODELS)
