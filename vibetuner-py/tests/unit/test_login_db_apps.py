# ABOUTME: Tests for DB-backed OAuth apps appearing on the login page.
# ABOUTME: Verifies that active apps for providers with login routes are surfaced.
# ruff: noqa: S101
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr
from vibetuner.config import settings
from vibetuner.frontend.oauth import (
    _PROVIDERS,
    PROVIDER_IDENTIFIERS,
    auto_register_providers,
    get_db_oauth_apps,
    register_oauth_provider,
)
from vibetuner.models.oauth import OauthProviderModel


@pytest.fixture(autouse=True)
def clean_provider_registry():
    """Clear provider registry before and after each test."""
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()
    yield
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()


def _fake_app(provider: str, name: str) -> MagicMock:
    """Create a fake OAuthProviderAppModel-like object for testing."""
    app = MagicMock()
    app.provider = provider
    app.name = name
    return app


class TestGetDbOauthApps:
    """Tests for get_db_oauth_apps()."""

    @pytest.mark.asyncio
    async def test_returns_apps_for_registered_providers(self, monkeypatch):
        """Active apps for providers with login routes appear in the result."""
        monkeypatch.setattr(settings, "google_client_id", SecretStr("test-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("test-secret"))
        auto_register_providers(["google"])

        app = _fake_app("google", "Acme Corp")

        with patch("vibetuner.models.oauth_app.OAuthProviderAppModel") as mock_model:
            mock_model.get_all_active = AsyncMock(return_value=[app])
            result = await get_db_oauth_apps()

        assert len(result) == 1
        assert result[0].name == "Acme Corp"
        assert result[0].provider == "google"

    @pytest.mark.asyncio
    async def test_excludes_apps_for_unregistered_providers(self, monkeypatch):
        """Apps for providers not in the registry are excluded."""
        monkeypatch.setattr(settings, "google_client_id", SecretStr("test-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("test-secret"))
        auto_register_providers(["google"])

        google_app = _fake_app("google", "My App")
        linkedin_app = _fake_app("linkedin", "Other App")

        with patch("vibetuner.models.oauth_app.OAuthProviderAppModel") as mock_model:
            mock_model.get_all_active = AsyncMock(
                return_value=[google_app, linkedin_app]
            )
            result = await get_db_oauth_apps()

        assert len(result) == 1
        assert result[0].provider == "google"

    @pytest.mark.asyncio
    async def test_excludes_apps_for_providers_without_login_routes(self):
        """Apps for providers with login_routes=False are excluded."""
        register_oauth_provider(
            "linkedin",
            OauthProviderModel(
                identifier="sub",
                params={"authorize_url": "https://example.com/auth"},
                client_kwargs={"scope": "openid"},
                config={
                    "LINKEDIN_CLIENT_ID": "id",
                    "LINKEDIN_CLIENT_SECRET": "secret",
                },
                login_routes=False,
            ),
        )

        app = _fake_app("linkedin", "LinkedIn App")

        with patch("vibetuner.models.oauth_app.OAuthProviderAppModel") as mock_model:
            mock_model.get_all_active = AsyncMock(return_value=[app])
            result = await get_db_oauth_apps()

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_apps(self, monkeypatch):
        """No active apps in the database means empty result."""
        monkeypatch.setattr(settings, "google_client_id", SecretStr("test-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("test-secret"))
        auto_register_providers(["google"])

        with patch("vibetuner.models.oauth_app.OAuthProviderAppModel") as mock_model:
            mock_model.get_all_active = AsyncMock(return_value=[])
            result = await get_db_oauth_apps()

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_providers_registered(self):
        """No registered providers means no apps shown, even if DB has apps."""
        app = _fake_app("google", "Some App")

        with patch("vibetuner.models.oauth_app.OAuthProviderAppModel") as mock_model:
            mock_model.get_all_active = AsyncMock(return_value=[app])
            result = await get_db_oauth_apps()

        assert result == []

    @pytest.mark.asyncio
    async def test_multiple_apps_for_same_provider(self, monkeypatch):
        """Multiple apps for the same provider are all returned."""
        monkeypatch.setattr(settings, "google_client_id", SecretStr("test-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("test-secret"))
        auto_register_providers(["google"])

        apps = [
            _fake_app("google", "Personal"),
            _fake_app("google", "Work"),
        ]

        with patch("vibetuner.models.oauth_app.OAuthProviderAppModel") as mock_model:
            mock_model.get_all_active = AsyncMock(return_value=apps)
            result = await get_db_oauth_apps()

        assert len(result) == 2
        names = {a.name for a in result}
        assert names == {"Personal", "Work"}
