---
paths:
  - src/**
  - templates/**
description: Development patterns for routes, models, services, templates, and HTMX
---

# Development Patterns

## Routes

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

**Shorthand**: `@render("template.html.jinja")` decorator — return a dict
instead of calling `render_template()`. Passes through `Response` objects
unchanged.

**Streaming**: `render_template_stream()` for large pages (improves TTFB).

Register routes in `__init__.py` via `APIRouter.include_router()`, then
list in `tune.py`.

## Models

```python
from beanie import Document, Link
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

Export from `__init__.py`, list in `tune.py` `models=[]`.

**Soft delete**: Use `DocumentWithSoftDelete` instead of `Document`.
`delete()` sets `deleted_at`, queries auto-filter deleted docs.
`hard_delete()` for permanent removal.

**Encrypted fields**: `EncryptedFieldsMixin` + `EncryptedStr` type
for transparent encrypt-on-save / decrypt-on-load. Requires
`FIELD_ENCRYPTION_KEY` env var. `vibetuner crypto set-key` to
configure, `vibetuner crypto rotate-key` to rotate.

## Services

No registration needed — just import where used. Email via
`vibetuner.services.email.EmailService`. Configure with
`MAIL_RESEND_API_KEY`, `MAIL_MAILJET_API_KEY` /
`MAIL_MAILJET_API_SECRET`, or `MAIL_CLOUDFLARE_API_TOKEN` /
`MAIL_CLOUDFLARE_ACCOUNT_ID` (public beta) in `.env`.

## Template Filters

Pass to `tune.py` as `template_filters={"name": func}`. Use
`markupsafe.Markup` for filters returning HTML.

## Middleware

Create `Middleware` list, pass to `tune.py` as `middleware=[]`.

## Rate Limiting

Built-in, enabled by default.
`from vibetuner.ratelimit import limiter`:

```python
@router.get("/api/search")
@limiter.limit("10/minute")
async def search(request: Request):  # request param required
    return {"results": []}

@router.get("/health")
@limiter.exempt
async def health(request: Request): ...
```

Configure via `RATE_LIMIT_*` env vars. Redis shares limits across
workers; falls back to in-memory.

## CLI Commands

Use `vibetuner.AsyncTyper` (never re-export `vibetuner.cli.app`).
Pass to `tune.py` `cli=`. Commands run as
`uv run vibetuner app <command>`.

## Custom Lifespan

**Frontend**: `@asynccontextmanager`, receives `FastAPI` app, yields
nothing. Wrap with `base_lifespan(app)`.
**Worker**: Takes no args, yields `Context`. Wrap with
`base_lifespan()`.

## CRUD Factory

```python
from vibetuner.crud import create_crud_routes, Operation
post_routes = create_crud_routes(
    Post, prefix="/api/posts", tags=["posts"],
    sortable_fields=["created_at"],
    filterable_fields=["status"],
    searchable_fields=["title", "content"],
    page_size=25,
)
```

Generates LIST/CREATE/READ/UPDATE/DELETE. Limit with `operations=`.
Hooks: `pre_create`, `post_create`, `pre_update`, `post_update`,
`pre_delete`, `post_delete` — all receive `request: Request`.

## Template Context Providers

```python
from vibetuner.rendering import register_globals
from vibetuner.rendering import register_context_provider

register_globals({"site_title": "My App"})

@register_context_provider
def dynamic_context() -> dict:
    return {"feature_flags": get_flags()}
```

## Runtime Configuration

`from vibetuner.runtime_config import register_config_value, get_config, set_config`.
Register with `register_config_value(key=, default=, value_type=,
category=, description=, is_secret=)`. Or declaratively in `tune.py`
via `runtime_config={...}`. Read with `await get_config("key")`.
Write with `await set_config("key", value)`.
Debug UI at `/debug/config`. CLI: `vibetuner config list|set|delete`.

**Built-in template globals**: `now` (UTC datetime), `today` (ISO
date string) — available in all templates automatically.

## Template Override

Create files in `templates/frontend/` or `templates/email/` to override
defaults.

## Debugging

`uv run vibetuner doctor` — validates project structure, config, env
vars, services, models, templates, deps.

`vibetuner debug open https://myapp.com` — generates HMAC-signed
magic link for production debug access (8-hour session, 5-min link
expiry). Uses `SESSION_KEY` from `.env`.

## Ad-hoc Database Operations

Uses `pymongo` (not `motor`). Use `AsyncMongoClient` and
`get_pymongo_collection()`. Existing documents may have `None` for
fields with Pydantic defaults — include `None` in filters.
