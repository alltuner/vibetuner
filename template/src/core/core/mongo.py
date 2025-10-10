from beanie import init_beanie
from pymongo import AsyncMongoClient

from core.models.registry import get_all_models

from .config import project_settings, settings


async def init_models() -> None:
    """Initialize MongoDB connection and register all Beanie models."""

    client: AsyncMongoClient = AsyncMongoClient(
        host=str(project_settings.mongodb_url),
        compressors=["zstd"],
    )

    await init_beanie(
        database=client[settings.mongo_dbname], document_models=get_all_models()
    )
