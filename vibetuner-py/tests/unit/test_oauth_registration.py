# ABOUTME: Tests for OAuth provider auto-registration from config.
# ABOUTME: Verifies builtin providers, env var handling, and route wiring.
# ruff: noqa: S101
import copy
import os
from unittest.mock import patch

import pytest
from loguru import logger
from vibetuner.frontend.oauth import (
    _BUILTIN_PROVIDERS,
    _PROVIDERS,
    PROVIDER_IDENTIFIERS,
    auto_register_providers,
    get_oauth_providers,
)
from vibetuner.frontend.routes.auth import register_oauth_routes, router


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

    def test_registers_with_env_vars(self):
        env = {
            "GOOGLE_CLIENT_ID": "test-id",
            "GOOGLE_CLIENT_SECRET": "test-secret",
        }
        with patch.dict(os.environ, env, clear=False):
            auto_register_providers(["google"])

        assert "google" in get_oauth_providers()
        assert PROVIDER_IDENTIFIERS["google"] == "sub"

    def test_skips_missing_env_vars(self, log_sink):
        auto_register_providers(["google"])

        assert "google" not in get_oauth_providers()
        log_text = "\n".join(log_sink)
        assert "GOOGLE_CLIENT_ID" in log_text

    def test_skips_unknown_provider(self, log_sink):
        auto_register_providers(["myspace"])

        assert "myspace" not in get_oauth_providers()
        log_text = "\n".join(log_sink)
        assert "myspace" in log_text

    def test_partial_env_vars(self):
        """Only client ID set, no secret."""
        env = {"GITHUB_CLIENT_ID": "just-id"}
        with patch.dict(os.environ, env, clear=False):
            auto_register_providers(["github"])

        assert "github" not in get_oauth_providers()

    def test_multiple_providers(self):
        env = {
            "GOOGLE_CLIENT_ID": "g-id",
            "GOOGLE_CLIENT_SECRET": "g-secret",
            "GITHUB_CLIENT_ID": "gh-id",
            "GITHUB_CLIENT_SECRET": "gh-secret",
        }
        with patch.dict(os.environ, env, clear=False):
            auto_register_providers(["google", "github"])

        assert set(get_oauth_providers()) == {"google", "github"}

    def test_empty_list(self, log_sink):
        auto_register_providers([])

        assert get_oauth_providers() == []
        assert log_sink == []

    def test_does_not_mutate_builtins(self):
        """Builtin config dict should not be modified by registration."""
        google_before = copy.deepcopy(_BUILTIN_PROVIDERS["google"])

        env = {
            "GOOGLE_CLIENT_ID": "test-id",
            "GOOGLE_CLIENT_SECRET": "test-secret",
        }
        with patch.dict(os.environ, env, clear=False):
            auto_register_providers(["google"])

        google_after = _BUILTIN_PROVIDERS["google"]
        assert google_after.identifier == google_before.identifier
        assert google_after.config == google_before.config
        assert google_after.params == google_before.params


class TestOAuthRouteRegistration:
    """Tests for OAuth route wiring on auth.router."""

    def test_routes_added_after_registration(self):
        env = {
            "GOOGLE_CLIENT_ID": "test-id",
            "GOOGLE_CLIENT_SECRET": "test-secret",
        }
        with patch.dict(os.environ, env, clear=False):
            auto_register_providers(["google"])

        routes_before = len(router.routes)

        register_oauth_routes()

        routes_after = len(router.routes)
        # Two routes per provider: login + callback
        assert routes_after == routes_before + 2

        route_paths = [r.path for r in router.routes]
        assert "/auth/provider/google" in route_paths
        assert "/auth/login/provider/google" in route_paths
