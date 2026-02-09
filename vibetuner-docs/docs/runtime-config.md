# Runtime Configuration

A layered configuration system for managing application settings that can be changed at runtime and
optionally persisted to MongoDB.

!!! note "Package name convention"
    In all examples, `app` refers to your project's Python package (the directory under `src/`).
    The actual name depends on your project slug (e.g., `src/myproject/` for a project named
    "myproject").

## Overview

Runtime configuration provides a way to manage application settings that:

- Can be changed without redeploying the application
- Persist across server restarts (when MongoDB is available)
- Support in-memory overrides for debugging and testing
- Integrate with a debug UI for viewing and editing values

This is separate from `CoreConfiguration` (`.env` settings) which handles framework-level settings
loaded at startup.

## Quick Start

### 1. Register Configuration Values

Register your config values at module load time, typically in `src/app/config.py`:

```python
from vibetuner.runtime_config import register_config_value

# Boolean feature flag
register_config_value(
    key="features.dark_mode",
    default=False,
    value_type="bool",
    category="features",
    description="Enable dark mode for users",
)

# Integer limit
register_config_value(
    key="limits.max_uploads",
    default=10,
    value_type="int",
    category="limits",
    description="Maximum uploads per user per day",
)

# Float rate
register_config_value(
    key="api.rate_limit",
    default=100.0,
    value_type="float",
    category="api",
    description="API rate limit (requests per minute)",
)

# Secret value (masked in debug UI, not editable)
register_config_value(
    key="api.secret_key",
    default="default-key",
    value_type="str",
    category="api",
    description="API secret key",
    is_secret=True,
)

# JSON object
register_config_value(
    key="features.feature_flags",
    default={"beta": False, "experimental": False},
    value_type="json",
    category="features",
    description="Feature flags dictionary",
)
```

### 2. Access Configuration Values

Use the async `get_config` function to retrieve values:

```python
from vibetuner.runtime_config import get_config

async def some_handler():
    # Get config value with registered default
    dark_mode = await get_config("features.dark_mode")

    # Get with explicit fallback for unregistered keys
    max_items = await get_config("unknown.key", default=50)

    if dark_mode:
        return render_dark_theme()
    return render_light_theme()
```

### 3. View and Edit via Debug UI

Navigate to `/debug/config` to view all registered configuration values:

- View all config grouped by category
- See current values and their sources (default, mongodb, runtime override)
- Edit non-secret values (DEBUG mode only)
- Refresh cache from MongoDB

## Layered Resolution

Configuration values are resolved with the following priority (highest to lowest):

1. **Runtime overrides** - In-memory overrides set programmatically or via debug UI
2. **MongoDB values** - Persisted values that survive restarts
3. **Registered defaults** - Default values defined in code

```python
# Example: If the same key exists in all three layers
# registered default: False
# mongodb value: True
# runtime override: False
# Result: False (runtime override wins)
```

## Value Types

The following value types are supported:

| Type    | Description                        | Example                        |
|---------|------------------------------------|--------------------------------|
| `bool`  | Boolean true/false                 | `True`, `False`                |
| `int`   | Integer numbers                    | `42`, `-1`, `0`                |
| `float` | Floating-point numbers             | `3.14`, `100.0`                |
| `str`   | Text strings                       | `"hello"`, `"api-key"`         |
| `json`  | JSON-serializable objects/arrays   | `{"key": "value"}`, `[1,2,3]`  |

Values are automatically validated and converted when set.

## API Reference

### `register_config_value`

Register a configuration value with its default:

```python
register_config_value(
    key: str,              # Unique key using dot-notation
    default: Any,          # Default value if not overridden
    value_type: str,       # "str", "int", "float", "bool", "json"
    description: str = None,  # Human-readable description
    category: str = "general",  # Category for grouping in debug UI
    is_secret: bool = False,    # Mask value in UI, prevent editing
)
```

### `get_config`

Get a configuration value:

```python
await get_config(
    key: str,              # Config key to look up
    default: Any = None,   # Fallback if key not found
) -> Any
```

### `RuntimeConfig` Class

For advanced usage, access the `RuntimeConfig` class directly:

```python
from vibetuner.runtime_config import RuntimeConfig

# Set a runtime override (in-memory only)
await RuntimeConfig.set_runtime_override("key", "value")

# Clear a runtime override
await RuntimeConfig.clear_runtime_override("key")

# Persist a value to MongoDB
await RuntimeConfig.set_value(
    key="key",
    value="value",
    value_type="str",
    description="Description",
    category="category",
    is_secret=False,
)

# Refresh cache from MongoDB
await RuntimeConfig.refresh_cache()

# Check if cache is stale (TTL: 60 seconds)
is_stale = RuntimeConfig.is_cache_stale()

# Get all config entries with sources
entries = await RuntimeConfig.get_all_config()
```

## Debug UI

The debug UI at `/debug/config` provides:

### List View

- All registered config values grouped by category
- Current value and source indicator (default/mongodb/runtime)
- Value type badges
- Secret values masked with `*****`
- Edit links for non-secret values (DEBUG mode only)
- Refresh cache button

### Detail/Edit View

- Full details for a single config entry
- Edit form with appropriate input type based on value type
- Option to persist to MongoDB or set as runtime override only
- Clear runtime override button

## MongoDB Persistence

When MongoDB is configured (`MONGODB_URL` environment variable):

- Values edited via debug UI can be persisted to MongoDB
- Cache is automatically refreshed on application startup
- Changes survive server restarts

When MongoDB is not configured:

- All changes are stored in memory only
- Changes are lost on server restart
- A warning is displayed in the debug UI

## Caching

Config values from MongoDB are cached for 60 seconds to reduce database load:

- Cache is populated on application startup
- Use the "Refresh Cache" button in debug UI to force refresh
- Use `RuntimeConfig.refresh_cache()` programmatically

## Security Considerations

### Secret Values

Mark sensitive values with `is_secret=True`:

- Values are masked (`*****`) in the debug UI
- Values cannot be edited via the debug UI
- Values are still accessible programmatically

### Debug UI Access

The debug routes at `/debug/*` are protected:

- **DEBUG mode**: Always accessible
- **Production mode**: Requires magic cookie authentication via `/_unlock-debug?token=YOUR_TOKEN`
- Set `DEBUG_ACCESS_TOKEN` environment variable to enable production access

### Editing Restrictions

- Only non-secret values can be edited via the debug UI
- Editing is only allowed in DEBUG mode
- Production environments should use MongoDB directly for updates

## Best Practices

1. **Use descriptive keys** with dot-notation for organization: `features.dark_mode`,
   `limits.api_rate`

2. **Group related config** using categories for better organization in debug UI

3. **Document everything** with clear descriptions so other developers understand each setting

4. **Mark secrets appropriately** to prevent accidental exposure in debug UI

5. **Use appropriate types** for proper validation and UI rendering

6. **Register early** in application startup (e.g., `src/app/config.py`) to ensure values are
   available throughout the application

## Example: Feature Flags

A common use case is feature flags for gradual rollouts:

```python
# src/app/config.py
from vibetuner.runtime_config import register_config_value

register_config_value(
    key="features.new_dashboard",
    default=False,
    value_type="bool",
    category="features",
    description="Enable the new dashboard UI",
)

register_config_value(
    key="features.beta_api",
    default=False,
    value_type="bool",
    category="features",
    description="Enable beta API endpoints",
)

# src/app/frontend/routes/dashboard.py
from vibetuner.runtime_config import get_config

@router.get("/dashboard")
async def dashboard(request: Request):
    use_new_dashboard = await get_config("features.new_dashboard")

    if use_new_dashboard:
        return render_template("dashboard_v2.html.jinja", request)
    return render_template("dashboard.html.jinja", request)
```

## Next Steps

- [Development Guide](development-guide.md) - Build features with runtime config
- [Architecture](architecture.md) - System design overview
- [Authentication](authentication.md) - User authentication system
