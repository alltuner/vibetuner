# ABOUTME: Tests that a known placeholder SESSION_KEY fails closed in production.
# ABOUTME: Raises in prod, warns outside prod, for both the old and new placeholders.
# ruff: noqa: S101

import pytest
from pydantic import SecretStr
from vibetuner.config import (
    DEFAULT_SESSION_KEY_PLACEHOLDER,
    KNOWN_INSECURE_SESSION_KEYS,
    CoreConfiguration,
    ProjectConfiguration,
)


OLD_SESSION_KEY_PLACEHOLDER = "ct-!secret-must-change-me"


class TestSessionKeyGuard:
    """A known placeholder session key must never run in production."""

    def test_known_placeholders_include_old_and_new(self):
        # The historical placeholder must stay guarded so projects upgrading
        # from an older scaffold are caught on upgrade.
        assert OLD_SESSION_KEY_PLACEHOLDER in KNOWN_INSECURE_SESSION_KEYS
        assert DEFAULT_SESSION_KEY_PLACEHOLDER in KNOWN_INSECURE_SESSION_KEYS

    def test_placeholder_raises_in_production(self):
        with pytest.raises(ValueError, match="SESSION_KEY"):
            CoreConfiguration(
                project=ProjectConfiguration(),
                environment="prod",
                session_key=SecretStr(DEFAULT_SESSION_KEY_PLACEHOLDER),
            )

    def test_old_placeholder_raises_in_production(self):
        with pytest.raises(ValueError, match="SESSION_KEY"):
            CoreConfiguration(
                project=ProjectConfiguration(),
                environment="prod",
                session_key=SecretStr(OLD_SESSION_KEY_PLACEHOLDER),
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

    def test_old_placeholder_warns_outside_production(self, log_sink):
        config = CoreConfiguration(
            project=ProjectConfiguration(),
            environment="dev",
            session_key=SecretStr(OLD_SESSION_KEY_PLACEHOLDER),
        )
        assert config.session_key.get_secret_value() == OLD_SESSION_KEY_PLACEHOLDER
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
