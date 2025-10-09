# Core Module

Foundation utilities - **DO NOT MODIFY** these files directly.

## Configuration (`config.py`)

### Accessing Settings

```python
from .core.config import settings

settings.DEBUG              # bool
settings.DATABASE_URL       # str
settings.SECRET_KEY         # str
settings.ENVIRONMENT        # "development" | "production"
```

### Adding Custom Settings

```python
class Settings(BaseSettings):
    MY_API_KEY: str = "default-key"
    FEATURE_FLAG: bool = False
    MAX_UPLOAD_SIZE: int = 10_000_000
```

### Environment Variables

Settings load from (priority order):

1. Environment variables
2. `.env.local` (not in git)
3. `.env` (not in git)
4. Default values

```bash
# .env (NOT committed - local config)
DATABASE_URL=mongodb://localhost:27017/myapp
DEBUG=true

# .env.local (NOT committed - overrides .env)
SECRET_KEY=my-secret-key
AWS_ACCESS_KEY_ID=AKIA...
```

## Database (`mongo.py`)

```python
from .core.mongo import init_mongo

await init_mongo()   # Startup (called automatically)
```

## Other Core Modules

- `paths.py` - Asset and template path management
- `templates.py` - Static template rendering
- `time.py` - Time utilities (`utc_now()`, `age_in_timedelta()`)
- `context.py` - App-wide context
- `logging.py` - Centralized logging setup
- `versioning.py` - Dynamic version from git tags
