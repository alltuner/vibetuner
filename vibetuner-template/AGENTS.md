# Agent Guide

FastAPI + MongoDB + HTMX web application scaffolded from AllTuner's template.

## Executive Summary

**For frontend work**: Use the `/frontend-design` skill for building pages and components. It
creates distinctive, production-grade interfaces that avoid generic AI aesthetics.

**Key locations**:

- Routes: `src/app/frontend/routes/`
- Templates: `templates/frontend/`
- Models: `src/app/models/`
- CSS config: `config.css`

**Stack**: HTMX for interactivity (not JavaScript frameworks), Tailwind classes in templates.

**Never modify**:

- `vibetuner` package code (installed dependency, not in your repo)
- `assets/statics/css/bundle.css` or `js/bundle.js` (auto-generated)

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
just local-all               # Runs server + assets with auto-port (recommended)
just local-all-with-worker   # Includes background worker (requires Redis)
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

#### Parallel Development

Work on multiple features simultaneously using isolated worktrees:

```bash
just feature-new NAME        # Create isolated worktree with new branch from main
just feature-list            # List all active feature worktrees
just feature-done [NAME]     # Remove worktree and delete merged branch
just feature-drop [NAME]     # Force remove worktree and delete branch (even if unmerged)
just feature-rebase          # Sync current branch with origin/main
```

The `NAME` parameter for `feature-done` and `feature-drop` is optional. If omitted, the command
auto-detects the current worktree. You can also pass a directory path instead of a branch name.

## Architecture

### Directory Structure

```text
src/
└── app/                       # ✅ YOUR APPLICATION CODE
    ├── config.py             # App-specific configuration
    ├── cli/                  # ✅ ADD YOUR CLI COMMANDS
    ├── frontend/             # ✅ ADD YOUR ROUTES
    │   └── routes/          # Your HTTP handlers
    ├── models/              # ✅ ADD YOUR MODELS
    ├── services/            # ✅ ADD YOUR SERVICES
    └── tasks/               # ✅ ADD YOUR BACKGROUND JOBS

templates/
├── frontend/              # ✅ YOUR CUSTOM FRONTEND TEMPLATES
├── email/                 # ✅ YOUR CUSTOM EMAIL TEMPLATES
└── markdown/              # ✅ YOUR CUSTOM MARKDOWN TEMPLATES

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

```python
# src/app/frontend/routes/dashboard.py
from fastapi import APIRouter, Request, Depends
from vibetuner.frontend.deps import get_current_user
from vibetuner.frontend.templates import render_template

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    return render_template("dashboard.html.jinja", request, {"user": user})
```

### Adding Models

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

### Adding Services

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

### Runtime Configuration

For settings that can be changed at runtime without redeploying, use the runtime configuration system:

```python
# src/app/config.py - Register config values at module load time
from vibetuner.runtime_config import register_config_value

register_config_value(
    key="features.dark_mode",
    default=False,
    value_type="bool",
    category="features",
    description="Enable dark mode for users",
)

register_config_value(
    key="limits.max_uploads",
    default=10,
    value_type="int",
    category="limits",
    description="Maximum uploads per user per day",
)

# Mark sensitive values as secrets (masked in debug UI, not editable)
register_config_value(
    key="api.secret_key",
    default="default-key",
    value_type="str",
    category="api",
    description="API secret key",
    is_secret=True,
)
```

```python
# Access config values anywhere in your app
from vibetuner.runtime_config import get_config

async def some_handler():
    dark_mode = await get_config("features.dark_mode")
    max_uploads = await get_config("limits.max_uploads", default=5)

    if dark_mode:
        return render_dark_theme()
```

**Value types**: `bool`, `int`, `float`, `str`, `json`

**Resolution priority** (highest to lowest):

1. Runtime overrides (in-memory, for debugging)
2. MongoDB values (persistent)
3. Registered defaults (code)

**Debug UI**: Navigate to `/debug/config` to view and edit config values. Requires DEBUG mode or
magic cookie authentication in production.

### Adding Background Tasks

If background jobs are enabled, tasks use the `vibetuner.tasks.worker`:

```python
# src/app/tasks/emails.py
from vibetuner.tasks.worker import worker

@worker.task()
async def send_digest_email(user_id: str):
    # Task logic here
    return {"status": "sent"}

# Queue from routes:
# from app.tasks.emails import send_digest_email
# task = await send_digest_email.enqueue(user.id)
```

**Important**: Register tasks by importing them in `src/app/tasks/lifespan.py` within the lifespan context:

```python
# src/app/tasks/lifespan.py
from contextlib import asynccontextmanager
from vibetuner.tasks.lifespan import base_lifespan
from vibetuner.context import Context

@asynccontextmanager
async def lifespan():
    async with base_lifespan() as worker_context:
        # Import task modules HERE after the worker is initialized
        from . import emails  # noqa: F401

        yield Context(**worker_context.model_dump())
```

**Why not `__init__.py`?** Importing task modules in `__init__.py` causes circular imports because the worker
needs to import `lifespan.py` before it's fully initialized. See `src/app/tasks/AGENTS.md` for detailed
explanation.

### Template Override

To customize templates, create them in your templates directory:

```bash
# Create custom frontend templates
# templates/frontend/dashboard.html.jinja

# Create custom email templates
# templates/email/default/welcome.html.jinja

# Create custom markdown templates
# templates/markdown/default/terms.md.jinja
```

The template system searches `templates/{namespace}/` for your custom templates.

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

### Pydantic Settings

```python
from vibetuner.config import project_settings
from app.config import settings

# Project-level (read-only from vibetuner)
project_settings.project_slug
project_settings.project_name
project_settings.mongodb_url
project_settings.supported_languages

# Application-specific (your config)
settings.debug              # bool
settings.version           # str
settings.aws_access_key_id # SecretStr | None
```

## Testing

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

# ✅ GOOD
async def get_user_by_email(email: str) -> User | None:
    return await User.find_one(Eq(User.email, email))

# ❌ BAD
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
{# ✅ GOOD: Standard utilities #}
<div class="p-4 text-lg font-bold bg-blue-500">

{# ✅ GOOD: Arbitrary values for one-off custom values #}
<div class="text-[13px] bg-[#1DB954]">

{# ✅ GOOD: Arbitrary properties for animations #}
<div class="animate-fade-in [animation-delay:100ms]">

{# ✅ GOOD: Arbitrary values for complex gradients #}
<div class="bg-[radial-gradient(ellipse_at_top,rgba(242,100,48,0.08)_0%,transparent_50%)]">

{# ❌ BAD: Inline styles (djLint H021 will flag these) #}
<div style="animation-delay: 100ms">
<div style="background: radial-gradient(...)">
```

**Define reusable design tokens in `assets/statics/css/config.css`:**

```css
@theme {
  /* Custom colors */
  --color-brand-primary: #009ddc;
  --color-brand-secondary: #f26430;

  /* Custom shadows */
  --shadow-glow-primary: 0 0 80px rgba(0, 157, 220, 0.2);

  /* Custom animations */
  --animate-fade-in: fade-in 0.5s ease-out forwards;
}
```

Then use them in templates:

```jinja
<div class="text-brand-primary shadow-glow-primary animate-fade-in">
```

**Important:**

- Never use inline `style=""` attributes - djLint will flag these
- Use arbitrary values for one-off custom styles
- Extract to `@theme` only when values are reused across multiple templates
- Prefer Tailwind's arbitrary syntax over creating custom CSS classes

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
   auto-generated bundles containing minified CSS/JS from the build process. Reading them wastes
   context and provides no useful information. Edit `config.css` and `config.js` instead.

## Custom Project Instructions

Add project-specific notes here.
