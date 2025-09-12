
# Core Module

Foundation utilities - **DO NOT MODIFY** these files directly.

## Configuration (`config.py`)

### How Settings Work

The application uses Pydantic Settings for configuration management.
Settings are loaded from multiple sources in priority order:

1. **Environment variables** (highest priority)
2. **`.env.local` file** (local overrides, not in git)
3. **`.env` file** (project defaults, in git)
4. **Default values** in Settings class (lowest priority)

### Accessing Settings

```python
from .core.config import settings

# Access configuration values
settings.DEBUG              # bool: Debug mode
settings.DATABASE_URL       # str: MongoDB connection
settings.SECRET_KEY         # str: Session encryption
settings.ENVIRONMENT        # str: "development" or "production"
settings.AWS_ACCESS_KEY_ID  # Optional[str]: AWS credentials
```

### Adding Custom Settings

Extend the Settings class in `config.py`:

```python
class Settings(BaseSettings):
    # Your custom settings
    MY_API_KEY: str = "default-key"
    FEATURE_FLAG: bool = False
    MAX_UPLOAD_SIZE: int = 10_000_000
    
    # Type hints determine parsing
    RATE_LIMIT: int  # Parsed as integer
    ENABLE_CACHE: bool  # Parsed as boolean
    API_ENDPOINTS: list[str]  # Parsed as JSON list
```

### Environment Variable Naming

- Settings names become uppercase environment variables
- Nested settings use double underscore: `OAUTH__GOOGLE__CLIENT_ID`
- Lists/dicts can be JSON strings: `ALLOWED_HOSTS='["localhost", "example.com"]'`

### Configuration Files

```bash
# .env (committed to git - defaults)
DATABASE_URL=mongodb://localhost:27017/myapp
ENVIRONMENT=development
DEBUG=true

# .env.local (NOT in git - local overrides)
DATABASE_URL=mongodb://prod-server:27017/myapp
SECRET_KEY=my-secret-key-here
AWS_ACCESS_KEY_ID=AKIA...
```

## Database (`mongo.py`)

MongoDB connection management:

```python
from .core.mongo import init_mongo, close_mongo

# In lifespan or startup
await init_mongo()  # Connects and registers all models

# In shutdown
await close_mongo()
```

## Paths (`paths.py`)

Static asset and template path management:

```python
from .core.paths import (
    assets,           # Static files directory
    templates,        # Template root
    frontend_templates  # Frontend template paths (with fallback)
)
```

## Templates (`templates.py`)

Static template rendering with namespace/language support:

```python
from .core.templates import render_static_template

html = render_static_template(
    "invoice",
    namespace="email",  # Optional: subfolder
    lang="es",          # Optional: language
    context={"user": user}
)
```

## Time Utilities (`time.py`)

Time manipulation helpers:

```python
from .core.time import (
    utc_now,           # Current UTC time
    age_in_timedelta,  # Time since datetime
    format_duration    # Format seconds as MM:SS
)
```

## Context (`context.py`)

Application-wide context management:

```python
from .core.context import Context

ctx = Context()  # Loads from config
ctx.DEBUG        # Access context values
```

## Logging (`logging.py`)

Centralized logging configuration:

```python
from .core.logging import setup_logging
import logging

setup_logging()  # Call once at startup
logger = logging.getLogger(__name__)
logger.info("Application started")
```

## Versioning (`versioning.py`)

Dynamic version from git tags:

```python
from .core.versioning import get_version

version = get_version()  # e.g., "1.2.3"
```

## Package Management

Core dependencies are managed by scaffolding:

```bash
# DO NOT manually add deps to core modules
# Use the main pyproject.toml for app dependencies
uv sync                     # Sync all dependencies
```

## Important Notes

- These are scaffolding-managed files
- Extend functionality via services/models/frontend
- Updates come through `just update-scaffolding`
