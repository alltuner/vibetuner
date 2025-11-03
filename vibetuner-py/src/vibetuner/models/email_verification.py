"""Email verification model for magic link authentication.

WARNING: This is a scaffolding-managed file. DO NOT MODIFY directly.
Handles passwordless authentication via email verification tokens.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Self

from beanie import Document
from beanie.operators import Eq, Set
from pydantic import Field

from vibetuner.models.registry import register_model
from vibetuner.time import now


# Email verification token model
@register_model
class EmailVerificationTokenModel(Document):
    email: str = Field(
        ...,
        description="Email address requesting verification",
    )
    token: str = Field(
        ...,
        description="Secure random token for email verification",
    )
    expires_at: datetime = Field(
        ...,
        description="Token expiration timestamp",
    )
    used: bool = Field(
        default=False,
        description="Whether the token has been consumed",
    )

    class Settings:
        name = "email_verification_tokens"
        indexes = [
            [("token", 1)],
            [("email", 1)],
            [("expires_at", 1)],
        ]

    @classmethod
    async def create_token(cls, email: str, expires_minutes: int = 15) -> Self:
        """Create a new verification token for email login"""
        token = secrets.token_urlsafe(32)
        expires_at = now() + timedelta(minutes=expires_minutes)

        # Invalidate any existing tokens for this email
        await cls.find(Eq(cls.email, email)).update_many(Set({cls.used: True}))

        verification_token = cls(
            email=email, token=token, expires_at=expires_at, used=False
        )

        return await verification_token.insert()

    @classmethod
    async def verify_token(cls, token: str) -> Optional[Self]:
        """Verify and consume a token"""
        verification_token: Optional[Self] = await cls.find_one(
            Eq(cls.token, token), Eq(cls.used, False)
        )

        if not verification_token:
            return None

        # Ensure expires_at is timezone-aware for comparison
        expires_at = verification_token.expires_at
        if expires_at.tzinfo is None:
            from datetime import timezone

            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now():
            return None

        # Mark token as used
        verification_token.used = True
        return await verification_token.save()
