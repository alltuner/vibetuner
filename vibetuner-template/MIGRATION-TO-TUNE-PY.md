# Migration Guide: Explicit Configuration with tune.py

This guide helps you migrate a vibetuner project from the old magic import system to
the explicit `tune.py` configuration.

## What Changed

Vibetuner no longer auto-discovers your routes, models, middleware, template filters, etc.
Instead, you explicitly declare everything in a single `tune.py` file.

**Benefits:**

- Import errors surface immediately with clear messages
- IDE autocomplete and type checking work
- You see exactly what's loaded
- Consistent pattern for all components

## Migration Steps

### Step 1: Create tune.py

Create `src/{your_package}/tune.py`:

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp

app = VibetunerApp()
```

### Step 2: Migrate Routes

**Before:** Routes used `register_router()` or were auto-discovered.

**After:** Import routers and list them in `tune.py`.

```python
# In your routes file, just define the router normally:
# src/myapp/frontend/routes/home.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Hello"}
```

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp
from myapp.frontend.routes.home import router as home_router
from myapp.frontend.routes.api import router as api_router

app = VibetunerApp(
    routes=[home_router, api_router],
)
```

**Remove:** Any `register_router()` calls or `_registered_routers` usage.

### Step 3: Migrate Models

**Before:** Models used `@register_model` decorator.

**After:** Export models in `__init__.py` and list in `tune.py`.

```python
# src/myapp/models/__init__.py
from .user import User
from .post import Post

__all__ = ["User", "Post"]
```

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp
from myapp.models import User, Post

app = VibetunerApp(
    models=[User, Post],
)
```

**Remove:** `@register_model` decorator from all model classes.

### Step 4: Migrate Template Filters

**Before:** Filters used `@register_filter` decorator.

**After:** Export filter functions and pass as dict to `tune.py`.

```python
# src/myapp/frontend/templates.py
def format_currency(value: float) -> str:
    return f"${value:,.2f}"

def format_date(dt) -> str:
    return dt.strftime("%Y-%m-%d")
```

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp
from myapp.frontend.templates import format_currency, format_date

app = VibetunerApp(
    template_filters={
        "currency": format_currency,
        "date": format_date,
    },
)
```

**Remove:** `@register_filter` decorator and `_filter_registry` usage.

### Step 5: Migrate Middleware

**Before:** Middleware was auto-discovered from `app.frontend.middleware`.

**After:** Import middleware and list in `tune.py`.

```python
# src/myapp/frontend/middleware.py
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

cors = Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)
```

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp
from myapp.frontend.middleware import cors

app = VibetunerApp(
    middleware=[cors],
)
```

### Step 6: Migrate Lifespan (if custom)

**Before:** Lifespan was auto-discovered from `app.frontend.lifespan` or `app.tasks.lifespan`.

**After:** Pass lifespan functions explicitly to `tune.py`.

```python
# src/myapp/frontend/lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
```

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp
from myapp.frontend.lifespan import lifespan

app = VibetunerApp(
    frontend_lifespan=lifespan,
)
```

For worker lifespan:

```python
app = VibetunerApp(
    worker_lifespan=worker_lifespan,
)
```

### Step 7: Migrate Tasks

**Before:** Tasks were auto-discovered by importing the lifespan.

**After:** Keep `@worker.task()` decorator, list task functions in `tune.py`.

```python
# src/myapp/tasks/emails.py
from vibetuner.tasks import worker

@worker.task()
async def send_email(to: str, subject: str):
    ...
```

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp
from myapp.tasks.emails import send_email

app = VibetunerApp(
    tasks=[send_email],
)
```

### Step 8: Migrate CLI Commands (if any)

**Before:** CLI was auto-discovered from `app.cli`.

**After:** Pass Typer app to `tune.py`.

```python
# src/myapp/cli/__init__.py
import typer

cli = typer.Typer()

@cli.command()
def my_command():
    print("Hello")
```

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp
from myapp.cli import cli

app = VibetunerApp(
    cli=cli,
)
```

### Step 9: Migrate OAuth Providers (if any)

**Before:** OAuth was configured via environment variables only.

**After:** List providers in `tune.py` (still needs env vars for secrets).

```python
app = VibetunerApp(
    oauth_providers=["google", "github"],
)
```

## Files to Delete

After migration, you can delete these deprecated patterns:

1. Any `@register_model` decorators (just remove the decorator, keep the class)
2. Any `@register_filter` decorators (just remove the decorator, keep the function)
3. Any `register_router()` calls
4. Any files that only existed for auto-discovery hooks

## Complete Example

Here's a complete `tune.py` for a typical app:

```python
# src/myapp/tune.py
from vibetuner import VibetunerApp

# Models
from myapp.models import User, Post, Comment

# Frontend
from myapp.frontend.routes import app_router
from myapp.frontend.middleware import cors, rate_limiter
from myapp.frontend.templates import format_currency, format_date
from myapp.frontend.lifespan import lifespan

# Tasks
from myapp.tasks.emails import send_welcome_email, send_notification

# CLI
from myapp.cli import admin_commands

app = VibetunerApp(
    # Database models
    models=[User, Post, Comment],

    # Frontend
    routes=[app_router],
    middleware=[cors, rate_limiter],
    template_filters={
        "currency": format_currency,
        "date": format_date,
    },
    frontend_lifespan=lifespan,

    # Auth
    oauth_providers=["google"],

    # Background tasks
    tasks=[send_welcome_email, send_notification],

    # CLI extensions
    cli=admin_commands,
)
```

## Zero-Config Still Works

If your app doesn't need customization, you don't need `tune.py` at all.
Vibetuner will use sensible defaults:

- Core vibetuner models are registered
- Base lifespan handles MongoDB and SQLModel
- No custom routes, middleware, or filters

Just delete `tune.py` if you want pure defaults.

## Troubleshooting

### "ModuleNotFoundError" on startup

Good! This is the new behavior. The error message tells you exactly what's broken.
Fix the import and restart.

### "tune.py must export an 'app' object"

Make sure your `tune.py` has:

```python
app = VibetunerApp(...)
```

### "'app' must be a VibetunerApp instance"

Don't use a different variable type. It must be `VibetunerApp`.
