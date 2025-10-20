# Core Frontend Module

**IMMUTABLE SCAFFOLDING CODE** - This is the framework's core frontend infrastructure.

## What's Here

This module contains the scaffolding's core frontend components:

- **routes/** - Essential default routes (auth, health, debug, language, user, meta)
- **templates.py** - Template rendering with automatic context injection
- **deps.py** - FastAPI dependencies (authentication, language, etc.)
- **middleware.py** - Request/response middleware
- **oauth.py** - OAuth provider integration
- **email.py** - Magic link email authentication
- **lifespan.py** - Application startup/shutdown lifecycle
- **context.py** - Request context management
- **hotreload.py** - Development hot-reload support

## Important Rules

⚠️  **DO NOT MODIFY** these core frontend components directly.

**For changes to core frontend:**

- File an issue at `https://github.com/alltuner/scaffolding`
- Core changes benefit all projects using the scaffolding

**For your application routes:**

- Create them in `src/app/frontend/routes/` instead
- Import core components when needed:
  - `from vibetuner.frontend.deps import get_current_user`
  - `from vibetuner.frontend.templates import render_template`

## User Route Pattern (for reference)

Your application routes in `src/app/frontend/routes/` should follow this pattern:

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

## Template Rendering

```python
# Automatic context in every template:
{
    "request": request,
    "DEBUG": settings.DEBUG,
    "hotreload": hotreload,  # Dev mode
    # ... plus your custom context
}
```

### Template Filters

- `{{ datetime | timeago }}` - "2 hours ago"
- `{{ datetime | format_date }}` - "January 15, 2024"
- `{{ text | markdown }}` - Convert Markdown to HTML

## Core Dependencies Available

Import these from `vibetuner.frontend.deps`:

- `get_current_user` - Require authenticated user (raises 403 if not authenticated)
- `get_current_user_optional` - Optional auth check (returns None if not authenticated)
- `LangDep` - Current language from cookie/header
- `MagicCookieDep` - Magic link cookie for authentication

## HTMX Patterns

```html
<!-- Partial updates -->
<button hx-post="/api/action" hx-target="#result">Click</button>

<!-- Form submission -->
<form hx-post="/submit" hx-swap="outerHTML">...</form>

<!-- Polling -->
<div hx-get="/status" hx-trigger="every 2s">...</div>
```

## Default Routes Provided

The following routes are automatically available (DO NOT MODIFY):

- **/auth/*** - OAuth and magic link authentication
- **/health/ping** - Health check endpoint
- **/debug/** - Debug info (only in DEBUG mode)
- **/lang/** - Language selection
- **/user/** - User profile routes
- **/meta/** - Metadata endpoints

## Development

**CRITICAL**: Both processes required:

```bash
# Terminal 1: Frontend assets
bun dev

# Terminal 2: Backend server
just local-dev
```
