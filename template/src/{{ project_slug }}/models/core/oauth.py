"""OAuth account model for third-party authentication providers.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
Manages OAuth provider accounts (Google, GitHub, etc.) linked to users.
"""

from typing import Self

from beanie import Document
from beanie.operators import Eq
from pydantic import Field

from . import FromIDMixin, TimeStampMixin


class OAuthAccountModel(Document, TimeStampMixin, FromIDMixin):
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
