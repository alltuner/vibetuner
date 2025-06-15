from typing import Optional, Self

from beanie import Document
from beanie.operators import Eq
from pydantic import Field

from .mixins import TimestampMixIn


class OAuthAccount(Document, TimestampMixIn):
    provider: str = Field(
        ...,
        description="OAuth provider name (google, github, twitter, etc.)",
    )
    provider_user_id: str = Field(
        ...,
        description="Unique user ID from the OAuth provider",
    )
    email: Optional[str] = Field(
        None,
        description="Email from OAuth provider",
    )
    name: Optional[str] = Field(
        None,
        description="Display name from OAuth provider",
    )
    picture: Optional[str] = Field(
        None,
        description="Profile picture URL",
    )

    class Settings:
        name = "oauth_accounts"

    @classmethod
    async def get_by_provider_and_id(
        cls,
        provider: str,
        provider_user_id: str,
    ) -> Self | None:
        return await cls.find_one(
            Eq(cls.provider, provider),
            Eq(cls.provider_user_id, provider_user_id),
        )
