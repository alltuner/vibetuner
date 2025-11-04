from beanie import init_beanie
from pymongo import AsyncMongoClient

from .config import settings
from .models.registry import get_all_models


async def init_models() -> None:
    """Initialize MongoDB connection and register all Beanie models."""

    client: AsyncMongoClient = AsyncMongoClient(
        host=str(settings.project.mongodb_url),
        compressors=["zstd"],
    )

    await init_beanie(
        database=client[settings.mongo_dbname], document_models=get_all_models()
    )
