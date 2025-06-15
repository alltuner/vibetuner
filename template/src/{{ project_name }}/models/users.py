from functools import cached_property
from typing import Any, List, Optional, Self

from beanie import Document
from beanie.operators import Eq
from pydantic import Field

from .mixins import TimeStampMixin
from .oauth import OAuthAccount


class UserModel(Document, TimeStampMixin):
    email: Optional[str] = Field(None, description="Primary email address")
    name: Optional[str] = Field(None, description="Display name")
    picture: Optional[str] = Field(None, description="Profile picture URL")
    oauth_accounts: List[OAuthAccount] = Field(default_factory=list)

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
