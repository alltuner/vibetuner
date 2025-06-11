from beanie import Document, View, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ._config import project_settings, settings
from .models.oauth import OAuthAccount
from .models.users import UserModel


models: list[type[Document] | type[View]] = [
    OAuthAccount,
    UserModel,
    # Custom models
]


async def init_models() -> None:
    """Initialize MongoDB connection and register all Beanie models."""

    mongo_db: AsyncIOMotorDatabase = AsyncIOMotorClient(
        host=str(project_settings.mongodb_url),
        compressors=["zstd"],
    )[settings.mongo_dbname]

    await init_beanie(database=mongo_db, document_models=models)
