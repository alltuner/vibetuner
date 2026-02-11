# ABOUTME: Tests for OAuth provider auto-registration from config.
# ABOUTME: Verifies builtin providers, settings-based credentials, and route wiring.
# ruff: noqa: S101
import copy

import pytest
from loguru import logger
from pydantic import SecretStr
from vibetuner.config import settings
from vibetuner.frontend.oauth import (
    _BUILTIN_PROVIDERS,
    _PROVIDERS,
    PROVIDER_IDENTIFIERS,
    auto_register_providers,
    get_oauth_providers,
)
from vibetuner.frontend.routes.auth import register_oauth_routes, router
from vibetuner.models.oauth import OauthProviderModel


@pytest.fixture(autouse=True)
def clean_provider_registry():
    """Clear provider registry before and after each test."""
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()
    yield
    _PROVIDERS.clear()
    PROVIDER_IDENTIFIERS.clear()


@pytest.fixture()
def log_sink():
    """Capture loguru output for assertion."""
    messages: list[str] = []
    sink_id = logger.add(lambda msg: messages.append(str(msg)), level="DEBUG")
    yield messages
    logger.remove(sink_id)


class TestBuiltinProviders:
    """Tests for the builtin provider configuration dict."""

    def test_google_defined(self):
        assert "google" in _BUILTIN_PROVIDERS
        google = _BUILTIN_PROVIDERS["google"]
        assert google.identifier == "sub"
        assert "openid" in google.client_kwargs["scope"]

    def test_github_defined(self):
        assert "github" in _BUILTIN_PROVIDERS
        github = _BUILTIN_PROVIDERS["github"]
        assert github.identifier == "id"
        assert "user:email" in github.client_kwargs["scope"]


class TestAutoRegisterProviders:
    """Tests for the auto_register_providers() function."""

    def test_registers_with_settings(self, monkeypatch):
        monkeypatch.setattr(settings, "google_client_id", SecretStr("test-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("test-secret"))

        auto_register_providers(["google"])

        assert "google" in get_oauth_providers()
        assert PROVIDER_IDENTIFIERS["google"] == "sub"

    def test_skips_missing_credentials(self, log_sink):
        auto_register_providers(["google"])

        assert "google" not in get_oauth_providers()
        log_text = "\n".join(log_sink)
        assert "google_client_id" in log_text

    def test_skips_unknown_provider(self, log_sink):
        auto_register_providers(["myspace"])

        assert "myspace" not in get_oauth_providers()
        log_text = "\n".join(log_sink)
        assert "myspace" in log_text

    def test_partial_credentials(self, monkeypatch):
        """Only client ID set, no secret."""
        monkeypatch.setattr(settings, "github_client_id", SecretStr("just-id"))

        auto_register_providers(["github"])

        assert "github" not in get_oauth_providers()

    def test_multiple_providers(self, monkeypatch):
        monkeypatch.setattr(settings, "google_client_id", SecretStr("g-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("g-secret"))
        monkeypatch.setattr(settings, "github_client_id", SecretStr("gh-id"))
        monkeypatch.setattr(settings, "github_client_secret", SecretStr("gh-secret"))

        auto_register_providers(["google", "github"])

        assert set(get_oauth_providers()) == {"google", "github"}

    def test_empty_list(self, log_sink):
        auto_register_providers([])

        assert get_oauth_providers() == []
        assert log_sink == []

    def test_does_not_mutate_builtins(self, monkeypatch):
        """Builtin config dict should not be modified by registration."""
        google_before = copy.deepcopy(_BUILTIN_PROVIDERS["google"])

        monkeypatch.setattr(settings, "google_client_id", SecretStr("test-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("test-secret"))
        auto_register_providers(["google"])

        google_after = _BUILTIN_PROVIDERS["google"]
        assert google_after.identifier == google_before.identifier
        assert google_after.config == google_before.config
        assert google_after.params == google_before.params


class TestCustomProviders:
    """Tests for custom OAuth provider registration."""

    def test_registers_custom_provider(self):
        custom = {
            "discord": OauthProviderModel(
                identifier="id",
                params={"authorize_url": "https://discord.com/oauth2/authorize"},
                client_kwargs={"scope": "identify email"},
                config={"DISCORD_CLIENT_ID": "test", "DISCORD_CLIENT_SECRET": "secret"},
            ),
        }
        auto_register_providers([], custom_providers=custom)

        assert "discord" in get_oauth_providers()
        assert PROVIDER_IDENTIFIERS["discord"] == "id"

    def test_custom_provider_skips_conflict(self, monkeypatch, log_sink):
        """Custom provider should not overwrite an already-registered builtin."""
        monkeypatch.setattr(settings, "google_client_id", SecretStr("g-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("g-secret"))

        custom = {
            "google": OauthProviderModel(
                identifier="custom-id",
                params={},
                client_kwargs={"scope": "custom"},
                config={},
            ),
        }
        auto_register_providers(["google"], custom_providers=custom)

        # Builtin google should win
        assert PROVIDER_IDENTIFIERS["google"] == "sub"
        log_text = "\n".join(log_sink)
        assert "conflicts" in log_text

    def test_custom_and_builtin_together(self, monkeypatch):
        monkeypatch.setattr(settings, "google_client_id", SecretStr("g-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("g-secret"))

        custom = {
            "twitter": OauthProviderModel(
                identifier="id",
                params={},
                client_kwargs={"scope": "tweet.read"},
                config={
                    "TWITTER_CLIENT_ID": "t-id",
                    "TWITTER_CLIENT_SECRET": "t-secret",
                },
            ),
        }
        auto_register_providers(["google"], custom_providers=custom)

        assert set(get_oauth_providers()) == {"google", "twitter"}

    def test_none_custom_providers(self):
        auto_register_providers([], custom_providers=None)
        assert get_oauth_providers() == []


class TestOAuthRouteRegistration:
    """Tests for OAuth route wiring on auth.router."""

    def test_routes_added_after_registration(self, monkeypatch):
        monkeypatch.setattr(settings, "google_client_id", SecretStr("test-id"))
        monkeypatch.setattr(settings, "google_client_secret", SecretStr("test-secret"))
        auto_register_providers(["google"])

        routes_before = len(router.routes)

        register_oauth_routes()

        routes_after = len(router.routes)
        # Two routes per provider: login + callback
        assert routes_after == routes_before + 2

        route_paths = [r.path for r in router.routes]
        assert "/auth/provider/google" in route_paths
        assert "/auth/login/provider/google" in route_paths
