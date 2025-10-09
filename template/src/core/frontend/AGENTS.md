# Frontend Module

FastAPI web application with HTMX-powered reactive UI.

## Quick Reference

**Add your routes**: `routes/*.py`
**Core routes** (DO NOT MODIFY): `default_routes/`

## Route Pattern

```python
from fastapi import APIRouter, Request, Depends
from ..deps import get_current_user
from ..templates import render_template

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

## Dependencies

- `get_current_user` - Require authenticated user
- `get_current_user_optional` - Optional auth check

## HTMX Patterns

```html
<!-- Partial updates -->
<button hx-post="/api/action" hx-target="#result">Click</button>

<!-- Form submission -->
<form hx-post="/submit" hx-swap="outerHTML">...</form>

<!-- Polling -->
<div hx-get="/status" hx-trigger="every 2s">...</div>
```

## Running

**CRITICAL**: Both processes required:

```bash
# Terminal 1: Frontend assets
bun dev

# Terminal 2: Backend server
just local-dev
```
