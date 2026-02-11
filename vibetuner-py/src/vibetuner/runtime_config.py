# ABOUTME: Layered runtime configuration system with MongoDB persistence.
# ABOUTME: Provides get/set config with priority: runtime overrides > MongoDB > registered defaults.

import json
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Literal, TypedDict

from vibetuner.config import settings
from vibetuner.logging import logger
from vibetuner.time import now


ConfigValueType = Literal["str", "int", "float", "bool", "json"]

# TTL for config cache in seconds
CACHE_TTL_SECONDS = 60


class ConfigRegistryEntry(TypedDict):
    """Type for registry entries."""

    default: Any
    value_type: ConfigValueType
    description: str | None
    category: str
    is_secret: bool


class ConfigEntry(TypedDict):
    """Type for config entries returned by get_all_config."""

    key: str
    value: Any
    value_type: ConfigValueType
    source: Literal["default", "mongodb", "runtime"]
    description: str | None
    category: str
    is_secret: bool


class RuntimeConfig:
    """Manages runtime configuration with layered resolution.

    Priority (highest to lowest):
    1. Runtime overrides - in-memory, for debugging/testing
    2. MongoDB values - persistent, survives restarts
    3. Registered defaults - defined in code
    """

    # Class-level storage
    _config_registry: dict[str, ConfigRegistryEntry] = {}
    _runtime_overrides: dict[str, Any] = {}
    _config_cache: dict[str, Any] = {}
    _cache_last_refresh: datetime | None = None

    @classmethod
    def is_cache_stale(cls) -> bool:
        """Check if cache needs refresh based on TTL."""
        if cls._cache_last_refresh is None:
            return True
        return now() - cls._cache_last_refresh > timedelta(seconds=CACHE_TTL_SECONDS)

    @classmethod
    async def refresh_cache(cls) -> None:
        """Reload all config values from MongoDB into cache."""
        cls._config_cache.clear()

        if settings.mongodb_url is None:
            logger.debug("MongoDB not available, config cache empty")
            cls._cache_last_refresh = now()
            return

        try:
            from vibetuner.models.config_entry import ConfigEntryModel

            entries = await ConfigEntryModel.find_all().to_list()
            for entry in entries:
                cls._config_cache[entry.key] = entry.value
            logger.debug(f"Config cache refreshed with {len(entries)} entries")
        except Exception as e:
            logger.warning(f"Failed to refresh config cache from MongoDB: {e}")

        cls._cache_last_refresh = now()

    @classmethod
    async def get(cls, key: str, default: Any = None) -> Any:
        """Get a config value with layered resolution.

        Priority:
        1. Runtime overrides
        2. MongoDB cache
        3. Registered default
        4. Provided default parameter
        """
        # 1. Check runtime overrides first (highest priority)
        if key in cls._runtime_overrides:
            return cls._runtime_overrides[key]

        # 2. Check MongoDB cache
        if key in cls._config_cache:
            return cls._config_cache[key]

        # 3. Check registered defaults
        if key in cls._config_registry:
            return cls._config_registry[key]["default"]

        # 4. Fall back to provided default
        return default

    @classmethod
    async def set_runtime_override(cls, key: str, value: Any) -> None:
        """Set a runtime override (in-memory only, highest priority)."""
        cls._runtime_overrides[key] = value
        logger.debug(f"Set runtime override: {key}")

    @classmethod
    async def clear_runtime_override(cls, key: str) -> None:
        """Remove a runtime override."""
        cls._runtime_overrides.pop(key, None)
        logger.debug(f"Cleared runtime override: {key}")

    @classmethod
    async def set_value(
        cls,
        key: str,
        value: Any,
        value_type: ConfigValueType,
        description: str | None = None,
        category: str = "general",
        is_secret: bool = False,
    ) -> None:
        """Persist a config value to MongoDB (or just cache if MongoDB unavailable)."""
        # Validate and convert value
        validated_value = cls._validate_value(value, value_type)

        # Update cache immediately
        cls._config_cache[key] = validated_value

        if settings.mongodb_url is None:
            logger.debug(f"MongoDB not available, config {key} stored in cache only")
            return

        try:
            from vibetuner.models.config_entry import ConfigEntryModel

            # Try to find existing entry
            existing = await ConfigEntryModel.find_one(ConfigEntryModel.key == key)

            if existing:
                existing.value = validated_value
                existing.value_type = value_type
                if description is not None:
                    existing.description = description
                existing.category = category
                existing.is_secret = is_secret
                await existing.save()
                logger.debug(f"Updated config entry: {key}")
            else:
                entry = ConfigEntryModel(
                    key=key,
                    value=validated_value,
                    value_type=value_type,
                    description=description,
                    category=category,
                    is_secret=is_secret,
                )
                await entry.insert()
                logger.debug(f"Created config entry: {key}")
        except Exception as e:
            logger.warning(f"Failed to persist config {key} to MongoDB: {e}")

    @classmethod
    async def delete_value(cls, key: str) -> bool:
        """Delete a config value from MongoDB."""
        # Remove from cache
        cls._config_cache.pop(key, None)

        if settings.mongodb_url is None:
            return True

        try:
            from vibetuner.models.config_entry import ConfigEntryModel

            result = await ConfigEntryModel.find_one(ConfigEntryModel.key == key)
            if result:
                await result.delete()
                logger.debug(f"Deleted config entry: {key}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to delete config {key} from MongoDB: {e}")
            return False

    @classmethod
    async def get_all_config(cls) -> list[ConfigEntry]:
        """Get all config entries with their sources for debug display."""
        entries: list[ConfigEntry] = []

        # Start with all registered configs
        for key, reg in cls._config_registry.items():
            # Determine value and source based on priority
            if key in cls._runtime_overrides:
                value = cls._runtime_overrides[key]
                source: Literal["default", "mongodb", "runtime"] = "runtime"
            elif key in cls._config_cache:
                value = cls._config_cache[key]
                source = "mongodb"
            else:
                value = reg["default"]
                source = "default"

            entries.append(
                ConfigEntry(
                    key=key,
                    value=value,
                    value_type=reg["value_type"],
                    source=source,
                    description=reg["description"],
                    category=reg["category"],
                    is_secret=reg["is_secret"],
                )
            )

        # Sort by category then key
        entries.sort(key=lambda e: (e["category"], e["key"]))
        return entries

    @classmethod
    def _validate_value(cls, value: Any, value_type: ConfigValueType) -> Any:
        """Validate and convert value to the specified type."""
        if value_type == "bool":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)

        if value_type == "int":
            return int(value)

        if value_type == "float":
            return float(value)

        if value_type == "str":
            return str(value)

        if value_type == "json":
            if isinstance(value, str):
                return json.loads(value)
            return value

        return value


def register_config_value(
    key: str,
    default: Any,
    value_type: ConfigValueType,
    description: str | None = None,
    category: str = "general",
    is_secret: bool = False,
) -> None:
    """Register a config value with its default.

    Call this at module load time to register config values that can be
    overridden at runtime via MongoDB or debug UI.

    Args:
        key: Unique key using dot-notation (e.g., 'features.dark_mode')
        default: Default value if not overridden
        value_type: Type for validation ('str', 'int', 'float', 'bool', 'json')
        description: Human-readable description
        category: Category for grouping in debug UI
        is_secret: If True, value is masked in debug UI and cannot be edited
    """
    RuntimeConfig._config_registry[key] = ConfigRegistryEntry(
        default=default,
        value_type=value_type,
        description=description,
        category=category,
        is_secret=is_secret,
    )


async def get_config(key: str, default: Any = None) -> Any:
    """Convenience function to get a config value.

    Args:
        key: Config key to look up
        default: Fallback if key not found in any layer

    Returns:
        Config value from highest priority source
    """
    return await RuntimeConfig.get(key, default)


def config_value(
    key: str,
    *,
    value_type: ConfigValueType = "str",
    description: str | None = None,
    category: str = "general",
    is_secret: bool = False,
) -> Callable[[Callable[[], Any]], Callable[[], Coroutine[Any, Any, Any]]]:
    """Decorator that registers a runtime config value.

    The decorated function provides the default value. At runtime, calling the
    decorated function returns the resolved value from the config layer stack
    (runtime override > MongoDB > registered default).

    Example::

        @config_value("features.dark_mode", value_type="bool", category="features")
        def dark_mode() -> bool:
            return False  # default

        # Later, in an async context:
        enabled = await dark_mode()
    """

    def decorator(func: Callable[[], Any]) -> Callable[[], Coroutine[Any, Any, Any]]:
        default = func()
        register_config_value(
            key=key,
            default=default,
            value_type=value_type,
            description=description or func.__doc__,
            category=category,
            is_secret=is_secret,
        )

        @wraps(func)
        async def wrapper() -> Any:
            return await RuntimeConfig.get(key, default)

        wrapper.key = key  # type: ignore[attr-defined]
        return wrapper

    return decorator


class ConfigGroup:
    """Base class for grouped config values with type-safe field access.

    Subclass and declare fields as ``ConfigField`` descriptors. All fields are
    auto-registered with ``RuntimeConfig`` when the class body is executed.

    Example::

        class FeatureFlags(ConfigGroup, category="features"):
            dark_mode = ConfigField(
                default=False, value_type="bool", description="Enable dark mode"
            )
            max_items = ConfigField(
                default=50, value_type="int", description="Max items per page"
            )

        # Later, in an async context:
        enabled = await FeatureFlags.dark_mode
    """

    def __init_subclass__(cls, category: str = "general", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._category = category
        for attr_name, field in list(vars(cls).items()):
            if isinstance(field, ConfigField):
                field._bind(cls, attr_name)


class ConfigField:
    """Descriptor that registers a single config value within a ``ConfigGroup``.

    Accessing the field on the class returns a coroutine that resolves the
    current value through the config layer stack.
    """

    def __init__(
        self,
        default: Any,
        value_type: ConfigValueType = "str",
        description: str | None = None,
        is_secret: bool = False,
    ) -> None:
        self.default = default
        self.value_type = value_type
        self.description = description
        self.is_secret = is_secret
        self.key: str | None = None

    def _bind(self, owner: type, name: str) -> None:
        category = getattr(owner, "_category", "general")
        self.key = f"{category}.{name}"
        register_config_value(
            key=self.key,
            default=self.default,
            value_type=self.value_type,
            description=self.description,
            category=category,
            is_secret=self.is_secret,
        )

    def __get__(self, obj: Any, objtype: type | None = None) -> Coroutine[Any, Any, Any]:
        return RuntimeConfig.get(self.key, self.default)  # type: ignore[arg-type]
