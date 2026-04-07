# ABOUTME: Tests for vibetuner.cli.config CLI commands.
# ABOUTME: Verifies list, set, and delete config commands without requiring MongoDB.
# ruff: noqa: S101
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner
from vibetuner.cli import app
from vibetuner.runtime_config import RuntimeConfig, register_config_value


runner = CliRunner()


@pytest.fixture(autouse=True)
def _clean_registry():
    """Reset RuntimeConfig state between tests."""
    orig_registry = RuntimeConfig._config_registry.copy()
    orig_cache = RuntimeConfig._config_cache.copy()
    orig_overrides = RuntimeConfig._runtime_overrides.copy()
    yield
    RuntimeConfig._config_registry.clear()
    RuntimeConfig._config_registry.update(orig_registry)
    RuntimeConfig._config_cache.clear()
    RuntimeConfig._config_cache.update(orig_cache)
    RuntimeConfig._runtime_overrides.clear()
    RuntimeConfig._runtime_overrides.update(orig_overrides)


def _register_test_configs():
    """Register a set of test config values."""
    register_config_value(
        key="features.dark_mode",
        default=False,
        value_type="bool",
        description="Enable dark mode",
        category="features",
    )
    register_config_value(
        key="secrets.api_key",
        default="",
        value_type="str",
        description="External API key",
        category="secrets",
        is_secret=True,
    )
    register_config_value(
        key="general.max_items",
        default=50,
        value_type="int",
        description="Max items per page",
        category="general",
    )


class TestConfigList:
    """Tests for `vibetuner config list`."""

    def test_list_shows_registered_configs(self):
        """list displays all registered config keys with their metadata."""
        _register_test_configs()

        with patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock):
            result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        assert "features.dark_mode" in result.output
        assert "secrets.api_key" in result.output
        assert "general.max_items" in result.output

    def test_list_shows_source(self):
        """list displays the value source (default, mongodb, runtime)."""
        _register_test_configs()

        with patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock):
            result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        assert "default" in result.output

    def test_list_masks_secret_values(self):
        """list masks secret values instead of showing them."""
        _register_test_configs()
        RuntimeConfig._config_cache["secrets.api_key"] = "sk-super-secret-key"

        with patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock):
            result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        assert "sk-super-secret-key" not in result.output

    def test_list_shows_non_secret_values(self):
        """list shows actual values for non-secret configs."""
        _register_test_configs()

        with patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock):
            result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        assert "50" in result.output

    def test_list_empty_registry(self):
        """list handles empty registry gracefully."""
        RuntimeConfig._config_registry.clear()

        with patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock):
            result = runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        assert "No config" in result.output


class TestConfigSet:
    """Tests for `vibetuner config set`."""

    def test_set_nonexistent_key_fails(self):
        """set rejects keys that aren't registered."""
        with patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock):
            result = runner.invoke(app, ["config", "set", "nonexistent.key"])

        assert result.exit_code == 1
        assert "not registered" in result.output.lower()

    def test_set_non_secret_with_value_arg(self):
        """set accepts a value argument for non-secret configs."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.set_value",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            result = runner.invoke(
                app, ["config", "set", "general.max_items", "--value", "100"]
            )

        assert result.exit_code == 0
        mock_set.assert_called_once()
        call_kwargs = mock_set.call_args
        assert call_kwargs.kwargs["key"] == "general.max_items"
        assert call_kwargs.kwargs["value"] == "100"

    def test_set_secret_prompts_for_value(self):
        """set prompts for hidden input when setting a secret without --value."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.set_value",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            result = runner.invoke(
                app, ["config", "set", "secrets.api_key"], input="my-secret-value\n"
            )

        assert result.exit_code == 0
        mock_set.assert_called_once()
        call_kwargs = mock_set.call_args
        assert call_kwargs.kwargs["value"] == "my-secret-value"

    def test_set_secret_with_value_arg_warns(self):
        """set warns about shell history when --value is used with a secret."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.set_value",
                new_callable=AsyncMock,
            ),
        ):
            result = runner.invoke(
                app,
                ["config", "set", "secrets.api_key", "--value", "sk-test"],
            )

        assert result.exit_code == 0
        assert "shell history" in result.output.lower()

    def test_set_preserves_registry_metadata(self):
        """set passes correct metadata from registry to set_value."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.set_value",
                new_callable=AsyncMock,
            ) as mock_set,
        ):
            result = runner.invoke(
                app, ["config", "set", "secrets.api_key"], input="my-key\n"
            )

        assert result.exit_code == 0
        call_kwargs = mock_set.call_args.kwargs
        assert call_kwargs["is_secret"] is True
        assert call_kwargs["category"] == "secrets"
        assert call_kwargs["value_type"] == "str"


class TestConfigDelete:
    """Tests for `vibetuner config delete`."""

    def test_delete_nonexistent_key_fails(self):
        """delete rejects keys that aren't registered."""
        with patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock):
            result = runner.invoke(app, ["config", "delete", "nonexistent.key"])

        assert result.exit_code == 1
        assert "not registered" in result.output.lower()

    def test_delete_calls_delete_value(self):
        """delete removes the value from MongoDB."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.delete_value",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_delete,
        ):
            result = runner.invoke(
                app, ["config", "delete", "features.dark_mode", "--yes"]
            )

        assert result.exit_code == 0
        mock_delete.assert_called_once_with("features.dark_mode")

    def test_delete_prompts_for_confirmation(self):
        """delete asks for confirmation by default."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.delete_value",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_delete,
        ):
            result = runner.invoke(
                app, ["config", "delete", "features.dark_mode"], input="y\n"
            )

        assert result.exit_code == 0
        mock_delete.assert_called_once()

    def test_delete_aborted_on_no(self):
        """delete aborts when user declines confirmation."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.delete_value",
                new_callable=AsyncMock,
            ) as mock_delete,
        ):
            result = runner.invoke(
                app, ["config", "delete", "features.dark_mode"], input="n\n"
            )

        assert result.exit_code == 0
        mock_delete.assert_not_called()

    def test_delete_not_found_in_db(self):
        """delete reports when value wasn't found in MongoDB."""
        _register_test_configs()

        with (
            patch("vibetuner.cli.config.init_mongodb", new_callable=AsyncMock),
            patch(
                "vibetuner.runtime_config.RuntimeConfig.delete_value",
                new_callable=AsyncMock,
                return_value=False,
            ),
        ):
            result = runner.invoke(
                app, ["config", "delete", "features.dark_mode", "--yes"]
            )

        assert result.exit_code == 0
        assert "not found" in result.output.lower()
