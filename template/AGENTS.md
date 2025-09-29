# Agent Guide

FastAPI + MongoDB + HTMX web application scaffolded from AllTuner's template.

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

### Common Commands

```bash
# Dependencies
uv add package-name          # Add Python package
just sync                    # Sync all dependencies

# Code Quality
ruff format .                # Format Python (ALWAYS run after code changes)
ruff check --fix .           # Auto-fix linting

# Localization
just extract-translations    # Extract i18n strings
just compile-locales         # Compile translations

# Versioning & Git
just bump-patch              # Version bump
just pr                      # Create pull request
```

## Architecture

### Directory Structure

```text
src/[project_slug]/
├── core/                # ⚠️  DO NOT MODIFY - scaffolding-managed
├── frontend/            # FastAPI app and routes
│   ├── routes/         # ✅ ADD YOUR ROUTES HERE
│   └── default_routes/ # ⚠️  DO NOT MODIFY
├── models/             # ✅ ADD YOUR MODELS HERE
│   └── core/          # ⚠️  DO NOT MODIFY
├── services/           # ✅ ADD YOUR SERVICES HERE
│   └── core/          # ⚠️  DO NOT MODIFY
├── tasks/              # Background jobs (if enabled)
└── cli/                # CLI commands

templates/frontend/
├── (your templates)    # ✅ ADD YOUR TEMPLATES HERE
└── defaults/          # ⚠️  DO NOT MODIFY - override by copying

assets/statics/
├── css/bundle.css     # Auto-generated from config.css
├── js/bundle.js       # Auto-generated from config.js
└── img/               # Your images
```

### Core Modules (DO NOT MODIFY)

- `core/`: Config, paths, logging, DB connection
- `models/core/`: User, OAuth, email verification
- `services/core/`: Email (SES), blob storage
- `frontend/default_routes/`: Auth, debug routes
- `templates/frontend/defaults/`: Base layouts

**To extend**: Create files in parent directories, never modify `core/` or `defaults/`

## Development Patterns

### Adding Routes

```python
# src/[project_slug]/frontend/routes/dashboard.py
from fastapi import APIRouter, Request, Depends
from ..deps import get_current_user
from ..templates import render_template

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    return render_template("dashboard.html.jinja", request, {"user": user})
```

### Adding Models

```python
# src/[project_slug]/models/post.py
from beanie import Document
from pydantic import Field
from .core.mixins import TimeStampMixin

class Post(Document, TimeStampMixin):
    title: str
    content: str
    author_id: str = Field(index=True)

    class Settings:
        name = "posts"
        indexes = ["author_id", "db_insert_dt"]
```

### Adding Services

```python
# src/[project_slug]/services/notifications.py
from .core.email import send_email

async def send_notification(user_email: str, message: str):
    await send_email(
        to_email=user_email,
        subject="Notification",
        html_content=f"<p>{message}</p>"
    )
```

### Adding Background Tasks

```python
# src/[project_slug]/tasks/emails.py
from .worker import worker

@worker.task()
async def send_digest_email(user_id: str):
    # Task logic here
    return {"status": "sent"}

# Queue from routes:
# task = await send_digest_email.enqueue(user.id)
```

### Template Override

To customize default templates, copy to parent directory:

```bash
# Override footer
cp templates/frontend/defaults/base/footer.html.jinja \
   templates/frontend/base/footer.html.jinja

# Now edit templates/frontend/base/footer.html.jinja
```

## Configuration

### Environment Variables

- `.env` - Default config (not committed)
- `.env.local` - Local overrides (not committed)

Key variables:

```bash
DATABASE_URL=mongodb://localhost:27017/[dbname]
REDIS_URL=redis://localhost:6379  # If background jobs enabled
SECRET_KEY=your-secret-key
DEBUG=true  # Development only
```

### Pydantic Settings

```python
from .core.config import settings

settings.DEBUG              # bool
settings.DATABASE_URL       # str
settings.ENVIRONMENT        # "development" | "production"
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

1. **Never modify** `core/` or `defaults/` directories
2. **Always run** `ruff format .` after Python changes
3. **Both processes required** for development: `bun dev` + `just local-dev`
4. **Use uv exclusively** for Python packages (never pip/poetry/conda)
5. **Override, don't modify** default templates

## Custom Project Instructions

Add project-specific notes here.
