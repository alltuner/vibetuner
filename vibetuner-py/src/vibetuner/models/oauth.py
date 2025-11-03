from typing import Self

from beanie import Document
from beanie.operators import Eq
from pydantic import BaseModel, Field

from vibetuner.models.registry import register_model

from .mixins import TimeStampMixin


class OauthProviderModel(BaseModel):
    identifier: str
    params: dict[str, str] = {}
    client_kwargs: dict[str, str]
    config: dict[str, str]


@register_model
class OAuthAccountModel(Document, TimeStampMixin):
    provider: str = Field(
        ...,
        description="OAuth provider name (google, github, twitter, etc.)",
    )
    provider_user_id: str = Field(
        ...,
        description="Unique user identifier from the OAuth provider",
    )
    email: str | None = Field(
        default=None,
        description="Email address retrieved from OAuth provider profile",
    )
    name: str | None = Field(
        default=None,
        description="Full display name retrieved from OAuth provider profile",
    )
    picture: str | None = Field(
        default=None,
        description="Profile picture URL retrieved from OAuth provider",
    )

    class Settings:
        name = "oauth_accounts"
        indexes = [
            [("provider", 1), ("provider_user_id", 1)],
        ]

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
