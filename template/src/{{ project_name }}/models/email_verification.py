import secrets
from datetime import datetime, timedelta
from typing import Optional, Self

from beanie import Document
from beanie.operators import Eq, Set

from ..time import now


# Email verification token model
class EmailVerificationToken(Document):
    email: str
    token: str
    expires_at: datetime
    used: bool = False

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

        verification_token = cls(email=email, token=token, expires_at=expires_at)

        return await verification_token.insert()

    @classmethod
    async def verify_token(cls, token: str) -> Optional[Self]:
        """Verify and consume a token"""
        verification_token = await cls.find_one(
            Eq(cls.token, token), Eq(cls.used, False)
        )

        if not verification_token:
            return None

        if verification_token.expires_at < datetime.utcnow():
            return None

        # Mark token as used
        verification_token.used = True
        return await verification_token.save()
