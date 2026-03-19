# ABOUTME: MongoDB model for OAuth app credentials.
# ABOUTME: Stores client_id/secret per provider, enabling multiple apps per provider.
from typing import Any, Self

from beanie import Document, Insert, Replace, Save, SaveChanges, Update, before_event
from beanie.operators import Eq
from pydantic import Field, model_validator

from .mixins import TimeStampMixin


class OAuthProviderAppModel(Document, TimeStampMixin):
    provider: str = Field(
        ...,
        description="References a registered OAuth provider (e.g. 'google', 'linkedin')",
    )
    name: str = Field(
        ...,
        description="Human-readable label (e.g. 'Personal', 'Acme Corp Page')",
    )
    client_id: str = Field(
        ...,
        description="OAuth client ID for this app",
    )
    client_secret: str = Field(
        ...,
        description="OAuth client secret for this app",
    )
    external_app_id: str | None = Field(
        default=None,
        description="Provider's own identifier for this app",
    )
    scopes: list[str] = Field(
        default_factory=list,
        description="Scopes to request; overrides provider defaults when non-empty",
    )
    capabilities: list[str] = Field(
        default_factory=list,
        description="Detected capabilities for this app",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this app is available for OAuth flows",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific extra data",
    )

    class Settings:
        name = "oauth_provider_apps"
        indexes = [
            [("provider", 1), ("name", 1)],
        ]

    # ── Transparent encryption ───────────────────────────────────

    @model_validator(mode="after")
    def _decrypt_secret_on_load(self) -> Self:
        from vibetuner.config import settings
        from vibetuner.crypto import decrypt_or_passthrough

        self.client_secret = decrypt_or_passthrough(
            self.client_secret, settings.oauth_encryption_key
        )
        return self

    @before_event(Insert)
    def _encrypt_on_insert(self) -> None:
        self._encrypt_secret()

    @before_event(Update, SaveChanges, Save, Replace)
    def _encrypt_on_update(self) -> None:
        self._encrypt_secret()

    def _encrypt_secret(self) -> None:
        from vibetuner.config import settings
        from vibetuner.crypto import encrypt_value, is_encrypted

        key = settings.oauth_encryption_key
        if key and not is_encrypted(self.client_secret):
            self.client_secret = encrypt_value(self.client_secret, key)

    # ── Queries ──────────────────────────────────────────────────

    @classmethod
    async def get_active_by_provider(cls, provider: str) -> list[Self]:
        return await cls.find(
            Eq(cls.provider, provider),
            Eq(cls.is_active, True),
        ).to_list()
