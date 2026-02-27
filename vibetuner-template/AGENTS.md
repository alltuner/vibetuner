# Agent Guide

FastAPI + MongoDB + HTMX web application scaffolded from AllTuner's template.

> **Package name**: Throughout this document, `app` is used as the package name in paths
> (`src/app/`) and imports (`from app.models import ...`). Your actual package name is the
> directory under `src/`, derived from your project slug. If your project is called "radar",
> replace `app` with `radar`: paths become `src/radar/`, imports become `from radar.models ...`.
> Check `ls src/` if unsure.

## Executive Summary

**For frontend work**: Use the `/frontend-design` skill for building pages and components. It
creates distinctive, production-grade interfaces that avoid generic AI aesthetics.

**Key locations**:

- Routes: `src/app/frontend/routes/`
- Templates: `templates/frontend/`
- Models: `src/app/models/`
- App config: `src/app/tune.py` (only if customizing)
- CSS config: `config.css`

**Stack**: HTMX for interactivity (not JavaScript frameworks), Tailwind classes in templates.

**Never modify**:

- `vibetuner` package code (installed dependency, not in your repo)
- `assets/statics/css/bundle.css` or `js/bundle.js` (auto-generated)

---

## Framework Documentation

For comprehensive vibetuner framework documentation, see:
https://vibetuner.alltuner.com/llms.txt

This URL provides AI-optimized documentation covering the full vibetuner API, patterns, and
best practices.

---

## Reporting Issues

The `vibetuner` package is a dependency you should not modify. For bugs, feature requests,
or ergonomic improvements:

- **File issues at**: <https://github.com/alltuner/vibetuner/issues>
- Include reproduction steps and relevant error messages
- Check existing issues before creating new ones
- If something feels harder than it should be, that's worth reporting too — we actively
  improve the framework based on real-world usage feedback

---

## Python Tooling

**IMPORTANT**: `uv` is the sole Python tool for this project. Never use `python`, `python3`, `pip`,
`poetry`, or `conda` directly. Always go through `uv run`:

```bash
uv run python script.py             # Run any ad-hoc Python script
uv run python -c "print('hello')"   # Run one-off Python expressions
uv run vibetuner run dev frontend   # Start dev server
uv run vibetuner scaffold update    # Update scaffolding
uv run ruff format .                # Format code
uv add package-name                 # Add a dependency
```

This ensures the correct virtual environment and dependencies are always available. If you need to
run any Python code (debugging, one-off scripts, REPL), use `uv run python`.

The `vibetuner[dev]` extra provides all development tools:

- `babel` - Translation extraction and compilation
- `djlint` - Jinja template formatting and linting
- `taplo` - TOML formatting
- `rumdl` - Markdown linting
- `granian[reload]` - ASGI server with hot reload

These are already included in scaffolded projects via `pyproject.toml`.

---

## Migration Guide

If migrating from an older vibetuner version that used auto-discovery:
See **MIGRATION-TO-TUNE-PY.md** in the project root for migration instructions.

---

## App Configuration (`tune.py`)

Vibetuner uses explicit configuration. You declare what your app uses in `tune.py`.

### Zero-Config Mode

New projects work out of the box with no configuration:

```bash
uv run vibetuner run dev frontend   # Works immediately
uv run vibetuner run dev worker     # Works immediately
```

### Adding Custom Components

When you need custom routes, models, etc., create `src/app/tune.py`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp

from app.frontend.routes import app_router
from app.models import Post, Comment

app = VibetunerApp(
    routes=[app_router],
    models=[Post, Comment],
)
```

### Full Configuration Example

```python
# src/app/tune.py
from vibetuner import VibetunerApp

# Explicit imports - errors surface immediately
from app.models import Post, Comment, Tag
from app.frontend.routes import app_router
from app.frontend.middleware import rate_limiter
from app.frontend.templates import format_date_catalan
from app.frontend.lifespan import lifespan
from app.tasks.notifications import send_notification
from app.cli import admin_commands

app = VibetunerApp(
    # Models (used by frontend and worker)
    models=[Post, Comment, Tag],

    # Frontend
    routes=[app_router],
    middleware=[rate_limiter],
    template_filters={"ca_date": format_date_catalan},
    frontend_lifespan=lifespan,

    # OAuth providers
    oauth_providers=["google", "github"],

    # Worker tasks
    tasks=[send_notification],

    # CLI extensions
    cli=admin_commands,
)
```

### Benefits

- **Clear errors**: Import errors show exact location (no hidden failures)
- **IDE support**: Autocomplete and type checking work
- **Explicit dependencies**: You see exactly what's loaded
- **Zero-config option**: Delete `tune.py` if you don't need customization

---

## PR Title Conventions for AI Assistants

This project uses **Release Please** for automated changelog generation and versioning.
When creating PRs, use **conventional commit format** for PR titles:

### Required Format

```text
<type>[optional scope]: <description>
```

### Supported Types

- `feat:` New features (triggers MINOR version)
- `fix:` Bug fixes (triggers PATCH version)
- `docs:` Documentation changes (triggers PATCH version)
- `chore:` Maintenance, dependencies (triggers PATCH version)
- `refactor:` Code refactoring (triggers PATCH version)
- `style:` Formatting, linting (triggers PATCH version)
- `test:` Test changes (triggers PATCH version)
- `perf:` Performance improvements (triggers MINOR version)
- `ci:` CI/CD changes (triggers PATCH version)
- `build:` Build system changes (triggers PATCH version)

### Breaking Changes

Add `!` to indicate breaking changes (triggers MAJOR version):

- `feat!: remove deprecated API`
- `fix!: change database schema`

### Examples

```text
feat: add OAuth authentication support
fix: resolve Docker build failure
docs: update installation guide
chore: bump FastAPI dependency
feat!: remove deprecated authentication system
```

### Why This Matters

- PR titles become commit messages after squash
- Every merged PR creates/updates a Release Please PR
- Release happens when the Release Please PR is merged
- Automatic changelog generation from PR titles
- Professional release notes for users

### Release Workflow

1. Merge any PR → Release Please creates/updates a release PR
2. Review the release PR (version bump + changelog)
3. Merge the release PR when ready to release
4. Release Please creates a GitHub release with a git tag
5. The git tag is automatically picked up by `uv-dynamic-versioning` for builds

### Versioning

This project uses **git tags** for versioning:

- Release Please manages git tags (e.g., `v1.2.3`)
- `uv-dynamic-versioning` reads the git tag to set package version
- No manual version file updates needed
- Build system automatically uses the latest git tag

## Tech Stack

**Backend**: FastAPI, MongoDB (Beanie ODM), Redis (optional)
**Frontend**: HTMX, Tailwind CSS, DaisyUI
**Tools**: uv (Python), bun (JS/CSS), Docker

## Quick Start

### Development (Local)

```bash
just install-deps            # Run once after cloning or updating lockfiles
just local-all               # Runs server + assets with auto-port (recommended)
just local-all-with-worker   # Includes background worker (requires Redis)
```

For projects using SQL models (SQLModel/SQLite/PostgreSQL), create tables first:

```bash
uv run vibetuner db create-schema   # Required once before first run
```

### Development (Docker)

```bash
just dev                     # All-in-one with hot reload
just worker-dev              # Background worker (if enabled)
```

### Justfile Commands

All project management tasks use `just` (command runner). Run `just` to see all available commands.

#### Development

```bash
just local-all               # Local dev: server + assets with auto-port (recommended)
just local-all-with-worker   # Local dev with background worker (requires Redis)
just dev                     # Docker development with hot reload
just local-dev PORT=8000     # Local server only (run bun dev separately)
just worker-dev              # Background worker only
```

**Local dev** requires MongoDB if using database features, and Redis if background jobs are enabled.
**Docker dev** runs everything in containers with automatic reload.

#### Dependencies

```bash
just install-deps            # Install from lockfiles
just update-repo-deps        # Update root scaffolding dependencies
just update-and-commit-repo-deps  # Update deps and commit changes
uv add package-name          # Add Python package
bun add package-name         # Add JavaScript package
```

#### Code Formatting

```bash
just format                  # Format ALL code (Python, Jinja, TOML, YAML)
just format-py               # Format Python with ruff
just format-jinja            # Format Jinja templates with djlint
just format-toml             # Format TOML files with taplo
just format-yaml             # Format YAML files with dprint
```

**IMPORTANT**: Always run `ruff format .` or `just format-py` after Python changes.

#### Code Linting

```bash
just lint                    # Lint ALL code
just lint-py                 # Lint Python with ruff
just lint-jinja              # Lint Jinja templates with djlint
just lint-md                 # Lint markdown files
just lint-toml               # Lint TOML files with taplo
just lint-yaml               # Lint YAML files with dprint
just type-check              # Type check Python with ty
```

#### Localization (i18n)

```bash
just i18n                    # Full workflow: extract, update, compile
just extract-translations    # Extract translatable strings
just update-locale-files     # Update existing .po files
just compile-locales         # Compile .po to .mo files
just new-locale LANG         # Create new language (e.g., just new-locale es)
just dump-untranslated DIR   # Export untranslated strings
```

#### CI/CD & Deployment

```bash
just build-dev               # Build development Docker image
just test-build-prod         # Test production build locally
just build-prod              # Build production image (requires clean tagged commit)
just release                 # Build and release production image
just deploy-latest HOST      # Deploy to remote host
```

#### Scaffolding Updates

```bash
just update-scaffolding      # Update project to latest vibetuner template
```

## Architecture

### Directory Structure

```text
src/
└── app/                       # YOUR APPLICATION CODE (created by you)
    ├── tune.py               # App configuration (optional, only if customizing)
    ├── config.py             # App-specific configuration (optional)
    ├── cli/                  # Your CLI commands
    ├── frontend/             # Your routes and frontend logic
    │   ├── routes/          # Your HTTP handlers
    │   ├── middleware.py    # Custom middleware (optional)
    │   ├── templates.py     # Custom template filters (optional)
    │   └── lifespan.py      # Custom startup/shutdown (optional)
    ├── models/              # Your Beanie document models
    ├── services/            # Your business logic
    └── tasks/               # Your background jobs

templates/
├── frontend/              # YOUR CUSTOM FRONTEND TEMPLATES
├── email/                 # YOUR CUSTOM EMAIL TEMPLATES
└── markdown/              # YOUR CUSTOM MARKDOWN TEMPLATES

assets/statics/
├── css/bundle.css          # Auto-generated from config.css
├── js/bundle.js            # Auto-generated from config.js
└── img/                    # Your images
```

### Core vs App

**`vibetuner` package** - Installed dependency (not in your repo)

- User authentication, OAuth, magic links
- Email service, blob storage
- Base templates, middleware, default routes
- MongoDB setup, logging, configuration
- **Changes**: File issues at `https://github.com/alltuner/vibetuner`

**`src/app/`** - Your application space

- Your business logic
- Your data models
- Your API routes
- Your background tasks
- Your CLI commands
- **Changes**: Edit freely, this is your code

## Development Patterns

### Adding Routes

Create routes in `src/app/frontend/routes/`, then register them in `tune.py`:

```python
# src/app/frontend/routes/dashboard.py
from fastapi import APIRouter, Request, Depends
from vibetuner import render_template
from vibetuner.frontend.deps import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    return render_template("dashboard.html.jinja", request, {"user": user})
```

```python
# src/app/frontend/routes/__init__.py
from fastapi import APIRouter
from .dashboard import router as dashboard_router
from .settings import router as settings_router

app_router = APIRouter()
app_router.include_router(dashboard_router)
app_router.include_router(settings_router)
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.frontend.routes import app_router

app = VibetunerApp(
    routes=[app_router],
)
```

### Adding Models

Create models in `src/app/models/`, then list them in `tune.py`:

```python
# src/app/models/post.py
from beanie import Document, Link
from pydantic import Field
from vibetuner.models import UserModel
from vibetuner.models.mixins import TimeStampMixin

class Post(Document, TimeStampMixin):
    title: str
    content: str
    author: Link[UserModel]

    class Settings:
        name = "posts"
        indexes = ["author", "db_insert_dt"]
```

```python
# src/app/models/__init__.py
from .post import Post
from .comment import Comment

__all__ = [Post, Comment]
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.models import Post, Comment

app = VibetunerApp(
    models=[Post, Comment],
)
```

### Adding Services

Services don't need registration - just import them where needed:

```python
# src/app/services/notifications.py
from vibetuner.services.email import send_email

async def send_notification(user_email: str, message: str):
    await send_email(
        to_email=user_email,
        subject="Notification",
        html_content=f"<p>{message}</p>"
    )
```

### Adding Template Filters

Create filter functions and pass them to `tune.py`:

```python
# src/app/frontend/templates.py
from datetime import datetime

def format_date_catalan(dt: datetime) -> str:
    """Format date in Catalan style."""
    return dt.strftime("%d/%m/%Y")

def truncate_words(text: str, max_words: int = 20) -> str:
    """Truncate text to max_words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.frontend.templates import format_date_catalan, truncate_words

app = VibetunerApp(
    template_filters={
        "ca_date": format_date_catalan,
        "truncate": truncate_words,
    },
)
```

Use in templates: `{{ post.created_at | ca_date }}` or `{{ post.content | truncate(30) }}`

**Filters returning HTML:** If your filter returns HTML markup, wrap the output
with `markupsafe.Markup` to prevent Jinja2 auto-escaping:

```python
from markupsafe import Markup, escape

def tag_badge(value: str) -> Markup:
    """Render a badge — escape user input, wrap result in Markup."""
    return Markup('<span class="badge">{}</span>').format(escape(value))
```

### Adding Middleware

Create middleware and pass to `tune.py`:

```python
# src/app/frontend/middleware.py
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=["https://example.com"],
        allow_methods=["*"],
    ),
]
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.frontend.middleware import middlewares

app = VibetunerApp(
    middleware=middlewares,
)
```

### Adding Background Tasks

Create tasks with the `@worker.task()` decorator, then list them in `tune.py`:

```python
# src/app/tasks/emails.py
from vibetuner.tasks.worker import get_worker

worker = get_worker()

@worker.task()
async def send_digest_email(user_id: str):
    # Task logic here
    return {"status": "sent"}
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.tasks.emails import send_digest_email

app = VibetunerApp(
    tasks=[send_digest_email],
)
```

Queue from routes:

```python
from app.tasks.emails import send_digest_email
task = await send_digest_email.enqueue(user.id)
```

### Adding CLI Commands

Create an `AsyncTyper` instance for your CLI commands. `AsyncTyper` extends `typer.Typer` with
native async support — use `async def` directly without `asyncio.run()` wrappers:

```python
# src/app/cli/__init__.py
from vibetuner import AsyncTyper

cli = AsyncTyper(help="My app CLI commands")

@cli.command()
async def seed(count: int = 10):
    """Seed the database with sample data."""
    from app.services.seeder import seed_database
    await seed_database(count)
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.cli import cli

app = VibetunerApp(
    cli=cli,
)
```

Commands are namespaced under `vibetuner app` (or your custom name):

```bash
uv run vibetuner app seed --count 50
```

> **Important:** Always create your own `AsyncTyper()` instance. Never re-export
> `vibetuner.cli.app` — that is the framework's root CLI and adding it back causes a
> circular reference.

### Custom Lifespan

For custom startup/shutdown logic, create a lifespan and pass to `tune.py`:

```python
# src/app/frontend/lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from vibetuner.frontend.lifespan import base_lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with base_lifespan(app):
        # Custom startup logic
        print("App starting with custom logic")
        yield
        # Custom shutdown logic
        print("App shutting down with custom logic")
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.frontend.lifespan import lifespan

app = VibetunerApp(
    frontend_lifespan=lifespan,
)
```

**Worker lifespan** (different signature — takes no arguments, yields context):

```python
# src/app/tasks/lifespan.py
from contextlib import asynccontextmanager
from vibetuner.tasks.lifespan import base_lifespan

@asynccontextmanager
async def lifespan():
    async with base_lifespan() as worker_context:
        # Custom worker startup logic
        print("Worker starting with custom logic")
        yield worker_context
        # Custom worker shutdown logic
        print("Worker shutting down")
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.tasks.lifespan import lifespan as worker_lifespan

app = VibetunerApp(
    worker_lifespan=worker_lifespan,
)
```

> **Note:** The frontend lifespan receives the `FastAPI` app and yields
> nothing. The worker lifespan takes no arguments and yields a `Context`
> object.

### CRUD Factory

Generate full CRUD endpoints for a Beanie model in one call:

```python
# src/app/frontend/routes/posts.py
from vibetuner.crud import create_crud_routes, Operation
from app.models import Post

post_routes = create_crud_routes(
    Post,
    prefix="/api/posts",
    tags=["posts"],
    sortable_fields=["created_at", "title"],
    filterable_fields=["status", "author_id"],
    searchable_fields=["title", "content"],
    page_size=25,
)
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.frontend.routes.posts import post_routes

app = VibetunerApp(routes=[post_routes])
```

This generates GET (list with pagination/filtering/sorting/search), POST (create),
GET `/{id}` (read), PATCH `/{id}` (update), DELETE `/{id}` endpoints.

Use `operations={Operation.LIST, Operation.READ}` to limit which endpoints are
generated. Use `create_schema`, `update_schema`, `response_schema` for custom
Pydantic models.

**Hook signatures:**

```python
from fastapi import Request

# Called before insert. Return modified data (or None to keep original).
async def pre_create(data: CreateSchema, request: Request) -> CreateSchema: ...

# Called after insert.
async def post_create(doc: MyModel, request: Request) -> None: ...

# Called before update. Return modified data (or None to keep original).
async def pre_update(doc: MyModel, data: UpdateSchema, request: Request) -> UpdateSchema: ...

# Called after update.
async def post_update(doc: MyModel, request: Request) -> None: ...

# Called before deletion.
async def pre_delete(doc: MyModel, request: Request) -> None: ...

# Called after deletion.
async def post_delete(doc: MyModel, request: Request) -> None: ...
```

### SSE (Server-Sent Events)

**IMPORTANT**: Import SSE helpers from `vibetuner.sse`, NOT `vibetuner.frontend.sse`.

```python
from vibetuner.sse import sse_endpoint, broadcast
```

**Channel-based endpoint (auto-subscribe):**

```python
from fastapi import APIRouter, Request
from vibetuner.sse import sse_endpoint

router = APIRouter()

@sse_endpoint("/events/notifications", channel="notifications", router=router)
async def notifications_stream(request: Request):
    pass  # channel kwarg handles everything
```

**Dynamic channel:**

```python
@sse_endpoint("/events/room/{room_id}", router=router)
async def room_stream(request: Request, room_id: str):
    return f"room:{room_id}"
```

**Broadcasting:**

```python
from vibetuner.sse import broadcast

# Raw HTML
await broadcast("notifications", "update", data="<div>New!</div>")

# With template
await broadcast(
    "feed", "new-post",
    template="partials/post.html.jinja",
    request=request,
    ctx={"post": post},
)
```

**HTMX client:**

```html
<div sse-connect="/events/notifications" sse-swap="update">
</div>
```

### Template Context Providers

Register variables available in every template render:

```python
# src/app/frontend/context.py
from vibetuner.rendering import register_globals, register_context_provider

register_globals({"site_title": "My App", "og_image": "/static/og.png"})

@register_context_provider
def dynamic_context() -> dict:
    return {"feature_flags": get_flags()}
```

### Runtime Configuration

For settings that can be changed at runtime without redeploying:

```python
# src/app/config.py
from vibetuner.runtime_config import register_config_value

register_config_value(
    key="features.dark_mode",
    default=False,
    value_type="bool",
    category="features",
    description="Enable dark mode for users",
)
```

```python
# Access config values anywhere
from vibetuner.runtime_config import get_config

async def some_handler():
    dark_mode = await get_config("features.dark_mode")
```

**Debug UI**: Navigate to `/debug/config` to view and edit config values.

### Template Override

To customize templates, create them in your templates directory:

```bash
# Create custom frontend templates
templates/frontend/dashboard.html.jinja

# Create custom email templates
templates/email/default/welcome.html.jinja
```

### Debugging with `vibetuner doctor`

Run diagnostics to validate your project setup:

```bash
uv run vibetuner doctor
```

Checks project structure, `tune.py` configuration, environment variables, service
connectivity (MongoDB, Redis, S3), models, templates, dependencies, and port
availability. Exits with code 1 if errors are found.

## Testing

Vibetuner provides pytest fixtures for testing. Fixtures are auto-discovered when
vibetuner is installed.

```python
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_dashboard(vibetuner_client, mock_auth):
    mock_auth.login(name="Alice", email="alice@example.com")
    resp = await vibetuner_client.get("/dashboard")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_signup_queues_email(vibetuner_client, mock_tasks):
    with patch(
        "app.tasks.emails.send_welcome_email",
        mock_tasks.send_welcome_email,
    ):
        resp = await vibetuner_client.post("/signup", data={...})
    assert mock_tasks.send_welcome_email.enqueue.called

@pytest.mark.asyncio
async def test_feature_flag(override_config):
    await override_config("features.dark_mode", True)
    from vibetuner.runtime_config import RuntimeConfig
    assert await RuntimeConfig.get("features.dark_mode") is True
```

**Available fixtures:**

- `vibetuner_client` — Async HTTP client with full middleware stack
- `vibetuner_app` — FastAPI app instance (override for custom apps)
- `vibetuner_db` — Temporary MongoDB database, dropped on teardown
- `mock_auth` — Mock authentication: `mock_auth.login(...)` / `.logout()`
- `mock_tasks` — Mock background tasks without Redis
- `override_config` — Override RuntimeConfig with auto-cleanup

### Prerequisites

The development server must be running:

```bash
just local-all
```

### Playwright MCP Integration

This project includes Playwright MCP for browser testing. The app runs on
`http://localhost:8000`.

**Authentication**: If testing protected routes, you'll need to authenticate
manually in the browser when prompted.

## Configuration

### Environment Variables

- `.env` - Configuration file (not committed)

Key variables:

```bash
DATABASE_URL=mongodb://localhost:27017/[dbname]
REDIS_URL=redis://localhost:6379  # If background jobs enabled
SECRET_KEY=your-secret-key
DEBUG=true  # Development only
```

### Vibetuner Settings

Vibetuner exposes a single `settings` object from `vibetuner.config`. It contains
framework-level configuration (`CoreConfiguration`) with project metadata nested
under `settings.project` (`ProjectConfiguration`).

```python
from vibetuner.config import settings

# --- Framework-level (CoreConfiguration) ---
settings.environment          # "dev" or "prod"
settings.debug                # True/False
settings.resolved_port        # Auto-calculated or explicit port
settings.expose_url           # External URL (from EXPOSE_URL env, or localhost)
settings.oauth_relay_url      # OAuth relay URL (from OAUTH_RELAY_URL env)
settings.mongodb_url          # MongoDB connection URL
settings.redis_url            # Redis connection URL (None if not configured)
settings.workers_available    # True if Redis is configured

# --- Project-level (ProjectConfiguration, read-only) ---
settings.project.project_slug
settings.project.project_name
settings.project.supported_languages
settings.project.default_language
settings.project.fqdn
```

For app-specific settings, create `src/app/config.py` with your own Pydantic
Settings class.

### Security Headers

Vibetuner includes built-in security headers middleware (enabled by default). It sets a
`Content-Security-Policy` with nonce-based script loading, plus standard hardening headers.

**Nonce usage in custom templates:**

Every request gets a unique CSP nonce stored in `request.state.csp_nonce`. Use it on any
`<script>` tag you add:

```html
<script nonce="{{ request.state.csp_nonce | default('') }}" src="/my-script.js"></script>
```

The `| default('')` filter ensures templates render safely even when the middleware is
disabled.

**Environment variables:**

| Variable | Default | Description |
|---|---|---|
| `CSP_ENABLED` | `true` | Enable/disable the security headers middleware |
| `CSP_EXTRA_SCRIPT_SRC` | `""` | Additional CSP script-src sources |
| `CSP_EXTRA_STYLE_SRC` | `""` | Additional CSP style-src sources |
| `CSP_EXTRA_FONT_SRC` | `""` | Additional CSP font-src sources |
| `CSP_EXTRA_CONNECT_SRC` | `""` | Additional CSP connect-src sources |
| `CSP_EXTRA_IMG_SRC` | `""` | Additional CSP img-src sources |
| `CSP_FRAME_ANCESTORS` | `'self'` | CSP frame-ancestors directive |

**Debug vs production:**

- **`DEBUG=true`**: Uses `Content-Security-Policy-Report-Only` so violations are logged
  in the browser console without blocking resources. This avoids breaking the dev
  hot-reload script.
- **`DEBUG=false`**: Uses the enforced `Content-Security-Policy` header.

**Important:** Avoid inline event handlers (`onclick`, `onload`, etc.) in your templates.
CSP with `strict-dynamic` blocks them. Use `addEventListener` or HTMX attributes instead.

## Localization

```bash
# 1. Extract translatable strings
just extract-translations

# 2. Update translation files
just update-locale-files

# 3. Translate in locales/[lang]/LC_MESSAGES/messages.po

# 4. Compile
just compile-locales
```

In templates:

```jinja
{% trans %}Welcome{% endtrans %}

{% trans user=user.name %}
Hello {{ user }}!
{% endtrans %}
```

In Python:

```python
from starlette_babel import gettext_lazy as _

message = _("Operation completed")
```

## Code Style

### Python

- **Type hints** always
- **Async/await** for DB operations
- **ALWAYS run `ruff format .` after code changes**
- Line length: 88 characters

```python
from beanie.operators import Eq

# GOOD
async def get_user_by_email(email: str) -> User | None:
    return await User.find_one(Eq(User.email, email))

# BAD
def get_usr(e):
    return User.find_one(User.email == e)  # Wrong: sync call, no types
```

### Frontend

- **HTMX** for dynamic updates
- **Tailwind classes** over custom CSS
- **DaisyUI components** when available
- Extend `base/skeleton.html.jinja` for layout

#### Tailwind CSS Best Practices

This project uses Tailwind CSS 4. Follow these patterns for maintainable styles:

**Use Tailwind utility classes directly in templates:**

```jinja
{# GOOD: Standard utilities #}
<div class="p-4 text-lg font-bold bg-blue-500">

{# GOOD: Arbitrary values for one-off custom values #}
<div class="text-[13px] bg-[#1DB954]">

{# GOOD: Arbitrary properties for animations #}
<div class="animate-fade-in [animation-delay:100ms]">

{# BAD: Inline styles (djLint H021 will flag these) #}
<div style="animation-delay: 100ms">
```

**Define reusable design tokens in `assets/statics/css/config.css`:**

```css
@theme {
  /* Custom colors */
  --color-brand-primary: #009ddc;
  --color-brand-secondary: #f26430;
}
```

Then use them in templates: `<div class="text-brand-primary">`

## MCP Servers Available

- **Playwright MCP**: Browser automation and testing (Chromium)
- **Cloudflare MCP**: Access to Cloudflare documentation and APIs
- **MongoDB MCP**: Direct database operations and queries
- **Chrome DevTools MCP**: Chrome DevTools Protocol integration

## Important Rules

1. **Never modify** the `vibetuner` package - It's an installed dependency
2. **File issues** at `https://github.com/alltuner/vibetuner` for core changes
3. **All your code** goes in `src/app/` - This is your space
4. **Always run** `ruff format .` after Python changes
5. **Start development** with `just local-all` (runs server + assets)
6. **Use uv exclusively** for Python packages (never pip/poetry/conda)
7. **Override, don't modify** core templates - create in `templates/` instead
8. **Never inspect** `assets/statics/css/bundle.css` or `assets/statics/js/bundle.js` - These are
   auto-generated bundles. Edit `config.css` and `config.js` instead.
9. **Configure in `tune.py`** - Don't rely on auto-discovery; explicitly list routes, models, etc.

## Improving Vibetuner

If you encounter anything in vibetuner that feels awkward, repetitive, or harder than it
should be — whether it's a missing API, unclear documentation, confusing error messages,
or any other ergonomic rough edge — please file an issue at
<https://github.com/alltuner/vibetuner/issues>. We actively improve the framework based
on real-world usage, and your feedback helps us prioritize what to fix next.

This applies to both **developers** and **AI agents**: if these instructions were unclear,
incomplete, or caused a mistake, that's a vibetuner bug we want to hear about.

## Custom Project Instructions

Add project-specific notes here.
