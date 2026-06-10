# ABOUTME: Tests that the default placeholder SESSION_KEY fails closed outside DEBUG.
# ABOUTME: Raises in production, warns loudly in debug, accepts a real key anywhere.
# ruff: noqa: S101

import pytest
from pydantic import SecretStr
from vibetuner.config import (
    DEFAULT_SESSION_KEY_PLACEHOLDER,
    CoreConfiguration,
    ProjectConfiguration,
)


class TestSessionKeyGuard:
    """The shipped placeholder session key must never run in production."""

    def test_placeholder_raises_in_production(self):
        with pytest.raises(ValueError, match="SESSION_KEY"):
            CoreConfiguration(
                project=ProjectConfiguration(),
                environment="prod",
                session_key=SecretStr(DEFAULT_SESSION_KEY_PLACEHOLDER),
            )

    def test_placeholder_warns_outside_production(self, log_sink):
        config = CoreConfiguration(
            project=ProjectConfiguration(),
            environment="dev",
            session_key=SecretStr(DEFAULT_SESSION_KEY_PLACEHOLDER),
        )
        assert config.session_key.get_secret_value() == DEFAULT_SESSION_KEY_PLACEHOLDER
        joined = "".join(log_sink)
        assert "SESSION_KEY" in joined

    def test_real_key_is_accepted_in_production(self):
        config = CoreConfiguration(
            project=ProjectConfiguration(),
            environment="prod",
            session_key=SecretStr("a-real-and-unique-secret-value"),
        )
        assert config.session_key.get_secret_value() == "a-real-and-unique-secret-value"

    def test_real_key_does_not_warn_outside_production(self, log_sink):
        CoreConfiguration(
            project=ProjectConfiguration(),
            environment="dev",
            session_key=SecretStr("a-real-and-unique-secret-value"),
        )
        joined = "".join(log_sink)
        assert "SESSION_KEY" not in joined
