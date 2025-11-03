"""Core user model for authentication and user management.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
Extend functionality by creating custom models that reference or extend these models.
"""

from functools import cached_property
from typing import Any, List, Self

from beanie import Document
from beanie.operators import Eq
from pydantic import BaseModel, Field
from pydantic_extra_types.language_code import LanguageAlpha2

from vibetuner.models.registry import register_model

from .mixins import TimeStampMixin
from .oauth import OAuthAccountModel
from .types import Link


class UserSettings(BaseModel):
    """User settings for the application.

    This class holds the default settings for the user, such as language and theme.
    It can be extended to include more user-specific settings in the future.
    """

    language: LanguageAlpha2 | None = Field(
        default=None,
        description="Preferred language for the user",
    )

    @cached_property
    def session_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the user settings for session storage.

        Make sure to only include fields that are necessary for the session.
        """
        return self.model_dump(
            exclude_none=True,
            exclude_unset=True,
            include={
                "language",
            },
        )


@register_model
class UserModel(Document, TimeStampMixin):
    email: str | None = Field(
        default=None,
        description="Primary email address for authentication",
    )
    name: str | None = Field(
        default=None,
        description="User's full display name",
    )
    picture: str | None = Field(
        default=None,
        description="URL to user's profile picture or avatar",
    )
    oauth_accounts: List[Link[OAuthAccountModel]] = Field(
        default_factory=list,
        description="Connected OAuth provider accounts (Google, GitHub, etc.)",
    )

    user_settings: UserSettings = Field(
        default_factory=UserSettings,
        description="User-specific settings for the application",
    )

    class Settings:
        name = "users"
        keep_nulls = False

    @cached_property
    def session_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            **self.model_dump(
                exclude_none=True,
                exclude_unset=True,
                include={"name", "email", "picture"},
            ),
            "settings": self.user_settings.session_dict,
        }

    @classmethod
    async def get_by_email(cls, email: str) -> Self | None:
        return await cls.find_one(Eq(cls.email, email))
