from functools import cached_property
from typing import Any, List, Self

from beanie import Document
from beanie.operators import Eq
from pydantic import Field

from ..mongo_types import Link
from . import OAuthAccountModel
from .mixins import TimeStampMixin


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

    class Settings:
        name = "users"

    @cached_property
    def session_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "picture": self.picture,
        }

    @classmethod
    async def get_by_email(cls, email: str) -> Self | None:
        return await cls.find_one(Eq(cls.email, email))
