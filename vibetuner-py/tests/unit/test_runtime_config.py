# ABOUTME: Tests for the RuntimeConfig service.
# ABOUTME: Validates layered config resolution, caching, and MongoDB persistence.
# ruff: noqa: S101
"""Tests for the RuntimeConfig service."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestConfigRegistry:
    """Tests for config value registration."""

    def test_register_config_value_stores_default(self):
        """register_config_value stores the default value in the registry."""
        from vibetuner.runtime_config import RuntimeConfig, register_config_value

        # Clear registry for test isolation
        RuntimeConfig._config_registry.clear()

        register_config_value(
            key="test.feature",
            default=True,
            value_type="bool",
            description="Test feature flag",
        )

        assert "test.feature" in RuntimeConfig._config_registry
        entry = RuntimeConfig._config_registry["test.feature"]
        assert entry["default"] is True
        assert entry["value_type"] == "bool"
        assert entry["description"] == "Test feature flag"

    def test_register_config_value_with_category(self):
        """register_config_value stores category."""
        from vibetuner.runtime_config import RuntimeConfig, register_config_value

        RuntimeConfig._config_registry.clear()

        register_config_value(
            key="features.dark_mode",
            default=False,
            value_type="bool",
            category="features",
            description="Enable dark mode",
        )

        entry = RuntimeConfig._config_registry["features.dark_mode"]
        assert entry["category"] == "features"

    def test_register_config_value_with_is_secret(self):
        """register_config_value stores is_secret flag."""
        from vibetuner.runtime_config import RuntimeConfig, register_config_value

        RuntimeConfig._config_registry.clear()

        register_config_value(
            key="api.secret_key",
            default="default-key",
            value_type="str",
            is_secret=True,
            description="API secret key",
        )

        entry = RuntimeConfig._config_registry["api.secret_key"]
        assert entry["is_secret"] is True


class TestGetConfig:
    """Tests for getting config values."""

    @pytest.mark.asyncio
    async def test_get_config_returns_registered_default(self):
        """get_config returns the registered default when no override exists."""
        from vibetuner.runtime_config import (
            RuntimeConfig,
            get_config,
            register_config_value,
        )

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        register_config_value(
            key="test.value",
            default=42,
            value_type="int",
        )

        result = await get_config("test.value")
        assert result == 42

    @pytest.mark.asyncio
    async def test_get_config_returns_fallback_for_unregistered_key(self):
        """get_config returns fallback for unregistered keys."""
        from vibetuner.runtime_config import RuntimeConfig, get_config

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        result = await get_config("unknown.key", "fallback")
        assert result == "fallback"

    @pytest.mark.asyncio
    async def test_get_config_returns_runtime_override_over_default(self):
        """Runtime override takes priority over registered default."""
        from vibetuner.runtime_config import (
            RuntimeConfig,
            get_config,
            register_config_value,
        )

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        register_config_value(
            key="test.override",
            default="default_value",
            value_type="str",
        )
        RuntimeConfig._runtime_overrides["test.override"] = "override_value"

        result = await get_config("test.override")
        assert result == "override_value"

    @pytest.mark.asyncio
    async def test_get_config_returns_cached_mongodb_value(self):
        """Cached MongoDB value takes priority over default."""
        from vibetuner.runtime_config import (
            RuntimeConfig,
            get_config,
            register_config_value,
        )

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        register_config_value(
            key="test.cached",
            default="default",
            value_type="str",
        )
        RuntimeConfig._config_cache["test.cached"] = "cached_value"

        result = await get_config("test.cached")
        assert result == "cached_value"

    @pytest.mark.asyncio
    async def test_get_config_priority_runtime_over_cache(self):
        """Runtime override takes priority over cached MongoDB value."""
        from vibetuner.runtime_config import (
            RuntimeConfig,
            get_config,
            register_config_value,
        )

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        register_config_value(
            key="test.priority",
            default="default",
            value_type="str",
        )
        RuntimeConfig._config_cache["test.priority"] = "cached"
        RuntimeConfig._runtime_overrides["test.priority"] = "runtime"

        result = await get_config("test.priority")
        assert result == "runtime"


class TestRuntimeOverrides:
    """Tests for runtime override management."""

    @pytest.mark.asyncio
    async def test_set_runtime_override(self):
        """set_runtime_override stores value in overrides dict."""
        from vibetuner.runtime_config import RuntimeConfig

        RuntimeConfig._runtime_overrides.clear()

        await RuntimeConfig.set_runtime_override("test.key", "test_value")

        assert RuntimeConfig._runtime_overrides["test.key"] == "test_value"

    @pytest.mark.asyncio
    async def test_clear_runtime_override(self):
        """clear_runtime_override removes value from overrides dict."""
        from vibetuner.runtime_config import RuntimeConfig

        RuntimeConfig._runtime_overrides["test.key"] = "value"

        await RuntimeConfig.clear_runtime_override("test.key")

        assert "test.key" not in RuntimeConfig._runtime_overrides


class TestCacheManagement:
    """Tests for cache TTL and refresh."""

    @pytest.mark.asyncio
    async def test_refresh_cache_clears_and_reloads(self):
        """refresh_cache clears existing cache and reloads from MongoDB."""
        from vibetuner.runtime_config import RuntimeConfig

        RuntimeConfig._config_cache["old.key"] = "old_value"
        RuntimeConfig._cache_last_refresh = None

        # Mock MongoDB not available
        with patch("vibetuner.runtime_config.settings") as mock_settings:
            mock_settings.mongodb_url = None
            await RuntimeConfig.refresh_cache()

        # Cache should be empty since no MongoDB
        assert RuntimeConfig._config_cache == {}

    @pytest.mark.asyncio
    async def test_is_cache_stale_returns_true_when_never_refreshed(self):
        """is_cache_stale returns True when cache was never refreshed."""
        from vibetuner.runtime_config import RuntimeConfig

        RuntimeConfig._cache_last_refresh = None

        assert RuntimeConfig.is_cache_stale() is True

    @pytest.mark.asyncio
    async def test_is_cache_stale_returns_false_when_fresh(self):
        """is_cache_stale returns False when cache is within TTL."""
        from vibetuner.runtime_config import RuntimeConfig
        from vibetuner.time import now

        RuntimeConfig._cache_last_refresh = now()

        assert RuntimeConfig.is_cache_stale() is False

    @pytest.mark.asyncio
    async def test_is_cache_stale_returns_true_when_expired(self):
        """is_cache_stale returns True when cache exceeds TTL."""
        from vibetuner.runtime_config import RuntimeConfig
        from vibetuner.time import now

        # Set last refresh to 2 minutes ago (TTL is 60 seconds)
        RuntimeConfig._cache_last_refresh = now() - timedelta(minutes=2)

        assert RuntimeConfig.is_cache_stale() is True


class TestGetAllConfig:
    """Tests for retrieving all config entries."""

    @pytest.mark.asyncio
    async def test_get_all_config_includes_registered_defaults(self):
        """get_all_config returns all registered config with sources."""
        from vibetuner.runtime_config import RuntimeConfig, register_config_value

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        register_config_value(
            key="feature.one",
            default=True,
            value_type="bool",
            category="features",
            description="Feature one",
        )
        register_config_value(
            key="feature.two",
            default=42,
            value_type="int",
            category="features",
            description="Feature two",
        )

        entries = await RuntimeConfig.get_all_config()

        assert len(entries) == 2
        assert entries[0]["key"] == "feature.one"
        assert entries[0]["value"] is True
        assert entries[0]["source"] == "default"

    @pytest.mark.asyncio
    async def test_get_all_config_shows_runtime_source(self):
        """get_all_config shows 'runtime' as source for overridden values."""
        from vibetuner.runtime_config import RuntimeConfig, register_config_value

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        register_config_value(
            key="test.key",
            default="default",
            value_type="str",
        )
        RuntimeConfig._runtime_overrides["test.key"] = "overridden"

        entries = await RuntimeConfig.get_all_config()

        entry = next(e for e in entries if e["key"] == "test.key")
        assert entry["value"] == "overridden"
        assert entry["source"] == "runtime"

    @pytest.mark.asyncio
    async def test_get_all_config_shows_mongodb_source(self):
        """get_all_config shows 'mongodb' as source for cached values."""
        from vibetuner.runtime_config import RuntimeConfig, register_config_value

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        register_config_value(
            key="test.key",
            default="default",
            value_type="str",
        )
        RuntimeConfig._config_cache["test.key"] = "from_mongo"

        entries = await RuntimeConfig.get_all_config()

        entry = next(e for e in entries if e["key"] == "test.key")
        assert entry["value"] == "from_mongo"
        assert entry["source"] == "mongodb"


class TestMongoDBIntegration:
    """Tests for MongoDB persistence."""

    @pytest.mark.asyncio
    async def test_set_value_persists_to_mongodb_when_available(self):
        """set_value persists to MongoDB when connection is available."""
        from vibetuner.runtime_config import RuntimeConfig

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        mock_model = MagicMock()
        mock_instance = MagicMock()
        mock_model.find_one = AsyncMock(return_value=None)
        mock_instance.insert = AsyncMock()

        with (
            patch("vibetuner.runtime_config.settings") as mock_settings,
            patch("vibetuner.models.config_entry.ConfigEntryModel", mock_model),
        ):
            mock_settings.mongodb_url = "mongodb://localhost:27017"
            mock_model.return_value = mock_instance

            await RuntimeConfig.set_value(
                key="test.key",
                value="test_value",
                value_type="str",
            )

        # Verify cache was updated
        assert RuntimeConfig._config_cache["test.key"] == "test_value"

    @pytest.mark.asyncio
    async def test_set_value_only_updates_cache_when_mongodb_unavailable(self):
        """set_value only updates cache when MongoDB is not available."""
        from vibetuner.runtime_config import RuntimeConfig

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        with patch("vibetuner.runtime_config.settings") as mock_settings:
            mock_settings.mongodb_url = None

            await RuntimeConfig.set_value(
                key="test.key",
                value="test_value",
                value_type="str",
            )

        # Cache should still be updated
        assert RuntimeConfig._config_cache["test.key"] == "test_value"


class TestValueTypeValidation:
    """Tests for value type validation and conversion."""

    @pytest.mark.asyncio
    async def test_validate_value_type_bool(self):
        """validate_value converts string to bool correctly."""
        from vibetuner.runtime_config import RuntimeConfig

        assert RuntimeConfig._validate_value("true", "bool") is True
        assert RuntimeConfig._validate_value("false", "bool") is False
        assert RuntimeConfig._validate_value("1", "bool") is True
        assert RuntimeConfig._validate_value("0", "bool") is False
        assert RuntimeConfig._validate_value(True, "bool") is True

    @pytest.mark.asyncio
    async def test_validate_value_type_int(self):
        """validate_value converts to int correctly."""
        from vibetuner.runtime_config import RuntimeConfig

        assert RuntimeConfig._validate_value("42", "int") == 42
        assert RuntimeConfig._validate_value(42, "int") == 42

    @pytest.mark.asyncio
    async def test_validate_value_type_float(self):
        """validate_value converts to float correctly."""
        from vibetuner.runtime_config import RuntimeConfig

        assert RuntimeConfig._validate_value("3.14", "float") == 3.14
        assert RuntimeConfig._validate_value(3.14, "float") == 3.14

    @pytest.mark.asyncio
    async def test_validate_value_type_str(self):
        """validate_value converts to str correctly."""
        from vibetuner.runtime_config import RuntimeConfig

        assert RuntimeConfig._validate_value(42, "str") == "42"
        assert RuntimeConfig._validate_value("hello", "str") == "hello"

    @pytest.mark.asyncio
    async def test_validate_value_type_json(self):
        """validate_value handles JSON correctly."""
        from vibetuner.runtime_config import RuntimeConfig

        result = RuntimeConfig._validate_value('{"key": "value"}', "json")
        assert result == {"key": "value"}

        result = RuntimeConfig._validate_value({"key": "value"}, "json")
        assert result == {"key": "value"}


class TestConfigValueDecorator:
    """Tests for the @config_value decorator."""

    def test_config_value_registers_key(self):
        """@config_value registers the key in the registry."""
        from vibetuner.runtime_config import RuntimeConfig, config_value

        RuntimeConfig._config_registry.clear()

        @config_value("test.decorator_key", value_type="bool", category="test")
        def my_flag() -> bool:
            return True

        assert "test.decorator_key" in RuntimeConfig._config_registry
        entry = RuntimeConfig._config_registry["test.decorator_key"]
        assert entry["default"] is True
        assert entry["value_type"] == "bool"
        assert entry["category"] == "test"

    def test_config_value_uses_docstring_as_description(self):
        """@config_value uses function docstring as description when none provided."""
        from vibetuner.runtime_config import RuntimeConfig, config_value

        RuntimeConfig._config_registry.clear()

        @config_value("test.docstring_key", value_type="str")
        def my_setting() -> str:
            """My setting description."""
            return "default"

        entry = RuntimeConfig._config_registry["test.docstring_key"]
        assert entry["description"] == "My setting description."

    def test_config_value_explicit_description_overrides_docstring(self):
        """Explicit description takes precedence over docstring."""
        from vibetuner.runtime_config import RuntimeConfig, config_value

        RuntimeConfig._config_registry.clear()

        @config_value(
            "test.explicit_desc", value_type="str", description="Explicit desc"
        )
        def my_setting() -> str:
            """Docstring desc."""
            return "default"

        entry = RuntimeConfig._config_registry["test.explicit_desc"]
        assert entry["description"] == "Explicit desc"

    @pytest.mark.asyncio
    async def test_config_value_returns_default(self):
        """Decorated function returns default when no overrides exist."""
        from vibetuner.runtime_config import RuntimeConfig, config_value

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        @config_value("test.deco_default", value_type="int")
        def max_retries() -> int:
            return 3

        result = await max_retries()
        assert result == 3

    @pytest.mark.asyncio
    async def test_config_value_returns_override(self):
        """Decorated function returns runtime override when set."""
        from vibetuner.runtime_config import RuntimeConfig, config_value

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        @config_value("test.deco_override", value_type="int")
        def max_retries() -> int:
            return 3

        RuntimeConfig._runtime_overrides["test.deco_override"] = 10

        result = await max_retries()
        assert result == 10

    def test_config_value_exposes_key_attribute(self):
        """Decorated function has .key attribute for introspection."""
        from vibetuner.runtime_config import RuntimeConfig, config_value

        RuntimeConfig._config_registry.clear()

        @config_value("test.key_attr", value_type="str")
        def my_val() -> str:
            return "val"

        assert my_val.key == "test.key_attr"


class TestConfigGroup:
    """Tests for the ConfigGroup class-based API."""

    def test_config_group_registers_fields(self):
        """ConfigGroup subclass auto-registers ConfigField entries."""
        from vibetuner.runtime_config import ConfigField, ConfigGroup, RuntimeConfig

        RuntimeConfig._config_registry.clear()

        class MyFlags(ConfigGroup, category="flags"):
            dark_mode = ConfigField(
                default=False, value_type="bool", description="Enable dark mode"
            )
            max_items = ConfigField(
                default=50, value_type="int", description="Max items per page"
            )

        assert "flags.dark_mode" in RuntimeConfig._config_registry
        assert "flags.max_items" in RuntimeConfig._config_registry

        dark = RuntimeConfig._config_registry["flags.dark_mode"]
        assert dark["default"] is False
        assert dark["value_type"] == "bool"
        assert dark["category"] == "flags"

        items = RuntimeConfig._config_registry["flags.max_items"]
        assert items["default"] == 50
        assert items["value_type"] == "int"

    @pytest.mark.asyncio
    async def test_config_group_field_access_returns_default(self):
        """Accessing a ConfigField returns the default via layered resolution."""
        from vibetuner.runtime_config import ConfigField, ConfigGroup, RuntimeConfig

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        class Settings(ConfigGroup, category="settings"):
            page_size = ConfigField(
                default=25, value_type="int", description="Page size"
            )

        result = await Settings.page_size
        assert result == 25

    @pytest.mark.asyncio
    async def test_config_group_field_access_returns_override(self):
        """Accessing a ConfigField returns the runtime override when set."""
        from vibetuner.runtime_config import ConfigField, ConfigGroup, RuntimeConfig

        RuntimeConfig._config_registry.clear()
        RuntimeConfig._runtime_overrides.clear()
        RuntimeConfig._config_cache.clear()

        class Settings(ConfigGroup, category="settings"):
            page_size = ConfigField(
                default=25, value_type="int", description="Page size"
            )

        RuntimeConfig._runtime_overrides["settings.page_size"] = 100

        result = await Settings.page_size
        assert result == 100

    def test_config_group_field_is_secret(self):
        """ConfigField with is_secret=True is registered as secret."""
        from vibetuner.runtime_config import ConfigField, ConfigGroup, RuntimeConfig

        RuntimeConfig._config_registry.clear()

        class Secrets(ConfigGroup, category="secrets"):
            api_key = ConfigField(
                default="changeme",
                value_type="str",
                description="API key",
                is_secret=True,
            )

        entry = RuntimeConfig._config_registry["secrets.api_key"]
        assert entry["is_secret"] is True
