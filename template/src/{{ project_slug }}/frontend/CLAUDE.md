# Frontend Module

FastAPI web application with HTMX-powered reactive UI.

## Structure

**Add your routes here:**

- `routes/*.py` - Application-specific endpoints

**Core routes (DO NOT MODIFY):**

- `default_routes/` - Auth, debug, language, user management

## Route Pattern

```python
from fastapi import APIRouter, Depends, Request
from ..deps import get_current_user
from ..templates import render_template

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    return render_template("dashboard.html.jinja", request, {"user": user})
```

## Template Rendering

### The `render_template()` Function

```python
from ..templates import render_template

def render_template(
    template: str,           # Template path (e.g., "index.html.jinja")
    request: Request,        # FastAPI request object
    ctx: dict | None = None, # Your custom context variables
    **kwargs                 # Additional response kwargs
) -> HTMLResponse
```

### Automatic Context Variables

Every template automatically receives:

```python
{
    # Always available
    "request": request,      # FastAPI Request object
    "DEBUG": settings.DEBUG, # Debug mode flag
    "hotreload": hotreload,  # Dev hot-reload script
    
    # From data_ctx (app-wide context)
    "APP_NAME": "YourApp",
    "VERSION": "1.0.0",
    # ... other Context values
    
    # Your custom context
    **ctx  # Variables you pass in
}
```

### Usage Examples

```python
@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    # Template gets: request, DEBUG, hotreload, user, stats
    return render_template(
        "dashboard.html.jinja",
        request,
        {"user": user, "stats": await get_stats()}
    )
```

### Available Template Filters

```jinja
{{ datetime_obj | timeago }}        # "2 hours ago"
{{ datetime_obj | format_date }}    # "January 15, 2024"  
{{ datetime_obj | format_datetime }} # "January 15, 2024 at 3:45 PM"
{{ text | markdown }}                # Convert Markdown to HTML
```

### Template Override Mechanism

Templates are searched in order:

1. `templates/frontend/` (your custom templates)
2. `templates/frontend/defaults/` (scaffolding defaults)

Override by creating same path without `defaults/`.

## Dependencies (`deps.py`)

- `get_current_user` - Require authenticated user
- `get_current_user_optional` - Optional auth check
- `get_streaq_client` - Background job queue client

## HTMX Patterns

```html
<!-- Partial updates -->
<button hx-post="/api/action" hx-target="#result">Click</button>

<!-- Form submission -->
<form hx-post="/submit" hx-swap="outerHTML">...</form>

<!-- Polling -->
<div hx-get="/status" hx-trigger="every 2s">...</div>
```

## Running the Application

**IMPORTANT**: You need TWO terminals for local development:

```bash
# Terminal 1: Watch and build frontend assets
pnpm dev

# Terminal 2: Run FastAPI server
just local-dev
```
