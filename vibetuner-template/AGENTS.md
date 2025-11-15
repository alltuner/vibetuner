# Agent Guide

FastAPI + MongoDB + HTMX web application scaffolded from AllTuner's template.

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

**CRITICAL**: Run both processes simultaneously:

```bash
# Terminal 1: Frontend asset building
bun dev

# Terminal 2: Backend server
just local-dev
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
just dev                     # Docker development with hot reload (recommended)
just local-dev PORT=8000     # Local development without Docker
just worker-dev              # Background worker (if background jobs enabled)
```

**Docker dev** runs everything in containers with automatic reload.
**Local dev** requires MongoDB/Redis running locally, but can be faster.

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
├── vibetuner/                 # ⚠️  IMMUTABLE SCAFFOLDING - DO NOT MODIFY
│   ├── frontend/             # Core web infrastructure
│   │   ├── routes/          # Default routes (auth, health, debug, etc.)
│   │   ├── deps.py          # Core dependencies
│   │   ├── templates.py     # Template rendering
│   │   ├── middleware.py    # Request/response middleware
│   │   └── oauth.py         # OAuth integration
│   ├── models/              # Core data models
│   │   ├── user.py         # User accounts
│   │   ├── oauth.py        # OAuth accounts
│   │   ├── email_verification.py
│   │   ├── blob.py         # File storage
│   │   └── mixins.py       # Reusable behaviors
│   ├── services/            # Core services
│   │   ├── email.py        # Email via SES
│   │   └── blob.py         # Blob storage
│   ├── tasks/               # Task infrastructure
│   ├── config.py            # Project configuration
│   ├── mongo.py             # Database setup
│   ├── logging.py           # Logging config
│   └── ... (other core utilities)
│
└── app/                       # ✅ YOUR APPLICATION CODE
    ├── config.py             # App-specific configuration
    ├── cli/                  # ✅ ADD YOUR CLI COMMANDS
    ├── frontend/             # ✅ ADD YOUR ROUTES
    │   └── routes/          # Your HTTP handlers
    ├── models/              # ✅ ADD YOUR MODELS
    ├── services/            # ✅ ADD YOUR SERVICES
    └── tasks/               # ✅ ADD YOUR BACKGROUND JOBS

templates/
├── app/                    # ✅ YOUR CUSTOM TEMPLATES
│   ├── frontend/          # Your frontend template overrides
│   ├── email/             # Your email template overrides
│   └── markdown/          # Your markdown template overrides
└── vibetuner/             # ⚠️  DO NOT MODIFY - scaffolding templates
    ├── frontend/          # Core frontend templates
    ├── email/             # Core email templates
    └── markdown/          # Core markdown templates

assets/statics/
├── css/bundle.css          # Auto-generated from config.css
├── js/bundle.js            # Auto-generated from config.js
└── img/                    # Your images
```

### Core vs App

**`src/vibetuner/`** - Immutable scaffolding framework

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

**Note**: `src/{{ project_slug }}/` exists for migration compatibility but is
deprecated. All new code goes in `src/app/`.

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

### Adding Background Tasks

```python
# src/app/tasks/emails.py
from app.tasks.worker import worker

@worker.task()
async def send_digest_email(user_id: str):
    # Task logic here
    return {"status": "sent"}

# Queue from routes:
# from app.tasks.emails import send_digest_email
# task = await send_digest_email.enqueue(user.id)
```

### Template Override

To customize core templates, override them in your templates directory:

```bash
# Override footer by creating the same structure in your templates/ directory
# templates/frontend/base/footer.html.jinja
```

The template system searches `templates/` first, then falls back to
`vibetuner/templates/` (from the package).

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

Both processes must be running:

```bash
# Terminal 1
bun dev

# Terminal 2
just local-dev
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

## MCP Servers Available

- **Playwright MCP**: Browser automation and testing (Chromium)
- **Cloudflare MCP**: Access to Cloudflare documentation and APIs
- **MongoDB MCP**: Direct database operations and queries
- **Chrome DevTools MCP**: Chrome DevTools Protocol integration

## Important Rules

1. **Never modify** `src/vibetuner/` - It's immutable scaffolding code
2. **File issues** at `https://github.com/alltuner/vibetuner` for core changes
3. **All your code** goes in `src/app/` - This is your space
4. **Always run** `ruff format .` after Python changes
5. **Both processes required** for development: `bun dev` + `just local-dev`
6. **Use uv exclusively** for Python packages (never pip/poetry/conda)
7. **Override, don't modify** core templates - create in `templates/` instead

## Custom Project Instructions

Add project-specific notes here.
