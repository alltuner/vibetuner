# Agent Guide

FastAPI + MongoDB + HTMX web application scaffolded from AllTuner's template.

> **Package name**: `app` below refers to your actual package under `src/`.
> Check `ls src/` if unsure.

## Executive Summary

**For frontend work**: Use the `/frontend-design` skill.
**Update scaffolding**: Use the `/update-scaffolding` skill.

**Key locations**:
Routes: `src/app/frontend/routes/` | Templates: `templates/frontend/` |
Models: `src/app/models/` | App config: `src/app/tune.py` | CSS config: `config.css`

**Stack**: HTMX + Tailwind + DaisyUI. No JavaScript frameworks.

**Never modify**: `vibetuner` package code |
`assets/statics/css/bundle.css` or `js/bundle.js` (auto-generated)

**Framework docs**: https://vibetuner.alltuner.com/llms.txt
**Report issues**: https://github.com/alltuner/vibetuner/issues

---

## Project Learnings (`LEARNINGS.md`)

If `LEARNINGS.md` exists, **read it before starting work**. Add non-obvious
discoveries as short dated bullet points. Remove stale entries.

---

## Python Tooling

**Use `uv` exclusively** (never `python`, `pip`, `poetry`, `conda`):

```bash
uv run python script.py             # Run scripts
uv run vibetuner run dev frontend   # Dev server
uv run ruff format .                # Format code
uv add package-name                 # Add dependency
```

Dev tools included via `vibetuner[dev]`: `babel`, `djlint`, `taplo`,
`rumdl`, `granian[reload]`.

---

## App Configuration (`tune.py`)

Zero-config works out of the box. For custom components, create
`src/app/tune.py`:

```python
from vibetuner import VibetunerApp
from app.frontend.routes import app_router
from app.models import Post, Comment

app = VibetunerApp(
    models=[Post, Comment],
    routes=[app_router],
    # Also supports: middleware, template_filters, frontend_lifespan,
    # worker_lifespan, oauth_providers, tasks, cli
)
```

---

## PR Titles & Releases

Use **conventional commits** for PR titles: `feat:`, `fix:`, `docs:`,
`chore:`, `refactor:`, `style:`, `test:`, `perf:`, `ci:`, `build:`.
Add `!` for breaking changes (e.g., `feat!:`). PR titles become squash
commit messages. Release Please auto-generates changelogs. Versioning
via git tags + `uv-dynamic-versioning`.

---

## Updating Scaffolding

Use the `/update-scaffolding` skill to update to the latest vibetuner
template. It checks for upstream changes, applies them in an isolated
worktree, resolves conflicts, and creates a PR.

```bash
# Interactive: invoke the skill inside Claude Code
/update-scaffolding

# Headless: run directly from the command line
claude -p "run the /update-scaffolding skill"
```

The skill will stop early if the scaffolding is already up to date.
If conflicts can't be auto-resolved, it leaves them flagged in the PR
for manual resolution.

For a one-command workflow that also updates dependencies:

```bash
just deps-scaffolding-pr     # Update deps + scaffolding and open a PR
```

---

## Quick Start

```bash
just install-deps            # Once after cloning
just local-all               # Dev server + assets (recommended)
just local-all-with-worker   # With background worker (requires Redis)
just dev                     # Docker development
```

Key commands: `just format` (all code), `just lint` (all code),
`just format-py` (Python only), `just i18n` (translations).

---

## Architecture

```text
src/app/              # Your code
  tune.py             # App config (optional)
  frontend/routes/    # HTTP handlers
  models/             # Beanie documents
  services/           # Business logic
  tasks/              # Background jobs
  cli/                # CLI commands
templates/frontend/   # Jinja templates
assets/statics/css/config.css  # Tailwind config (edit this, not bundle.css)
```

**Core (`vibetuner` package)**: Auth, OAuth, email, blob storage, base
templates, MongoDB setup. File issues, don't modify.
**App (`src/app/`)**: Your code. Edit freely.

---

## Development Patterns

### Routes

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

### Models

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

### Services

No registration needed — just import where used. Email via
`vibetuner.services.email.EmailService`. Configure with
`MAIL_RESEND_API_KEY` or `MAIL_MAILJET_API_KEY` /
`MAIL_MAILJET_API_SECRET` in `.env`.

### Template Filters

Pass to `tune.py` as `template_filters={"name": func}`. Use
`markupsafe.Markup` for filters returning HTML.

### Middleware

Create `Middleware` list, pass to `tune.py` as `middleware=[]`.

### Rate Limiting

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

### Background Tasks

```python
from vibetuner.tasks.worker import get_worker
worker = get_worker()

@worker.task()
async def send_digest_email(user_id: str): ...
```

List in `tune.py` `tasks=[]`. Queue with
`await send_digest_email.enqueue(user.id)`.

### CLI Commands

Use `vibetuner.AsyncTyper` (never re-export `vibetuner.cli.app`).
Pass to `tune.py` `cli=`. Commands run as
`uv run vibetuner app <command>`.

### Custom Lifespan

**Frontend**: `@asynccontextmanager`, receives `FastAPI` app, yields
nothing. Wrap with `base_lifespan(app)`.
**Worker**: Takes no args, yields `Context`. Wrap with
`base_lifespan()`.

### CRUD Factory

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

### SSE

**Import from `vibetuner.sse`** (NOT `vibetuner.frontend.sse`):

```python
from vibetuner.sse import sse_endpoint, broadcast

@sse_endpoint(
    "/events/notifications",
    channel="notifications",
    router=router,
)
async def notifications_stream(request: Request): pass

# Dynamic: return channel name from function body
# Broadcast: await broadcast("channel", "event",
#   data="<html>" or template=..., ctx=...)
# HTMX: <div sse-connect="/events/..." sse-swap="event-name">
```

### HTMX Response Headers

From `vibetuner.htmx`: `hx_redirect(url)`,
`hx_location(path, target=, swap=)`,
`hx_trigger(response, event, detail)`, `hx_push_url`,
`hx_replace_url`, `hx_reswap`, `hx_retarget`, `hx_refresh`,
`hx_trigger_after_settle`, `hx_trigger_after_swap`.

### HTMX 4 Event Handling

htmx 4 changed event handling significantly. Key differences:

**Event names** use colon-separated format (not camelCase):
`htmx:after:request`, `htmx:before:swap`, `htmx:after:settle`.

**`hx-on` attributes** — the `hx-on::` shorthand is broken in
alpha8. Use the explicit long form:

```html
<!-- BROKEN: hx-on::after-request="..." -->
<!-- WORKS: -->
<form hx-on:htmx:after:request="this.reset()">
```

**`event.detail`** was restructured. `event.detail.successful` no
longer exists. Use `event.detail.ctx.response` instead:

```javascript
// v2: event.detail.successful, event.detail.elt, event.detail.xhr
// v4: event.detail.ctx.response, event.detail.ctx.sourceElement,
//     event.detail.ctx.status
```

**Events do not bubble** to `document.body` in v4. Attach listeners
directly to elements or use `hx-on` attributes.

See the [HTMX migration guide](https://vibetuner.alltuner.com/htmx-migration/)
for full details.

### Response Caching (Server-Side)

`from vibetuner.cache import cache, invalidate, invalidate_pattern`.
`@cache(expire=60)` — Redis-backed, key from path+query params.
Disabled in debug mode (`force_caching=True` to override).
No-op without Redis.

### Cache Control (Browser-Side)

`from vibetuner.decorators import cache_control`.
`@cache_control(max_age=300, public=True)`. Supports: `public`,
`private`, `no_cache`, `no_store`, `max_age`, `s_maxage`,
`must_revalidate`, `stale_while_revalidate`, `immutable`.

### Block Rendering for HTMX Partials

`render_template_block("template.html.jinja", "block_name",
request, ctx)` — renders a single `{% block %}`.
`render_template_blocks(...)` (plural) for multi-block OOB swaps.

### HTMX Request Detection

`request.state.htmx` — truthy for HTMX requests. Properties:
`.boosted`, `.target`, `.trigger`, `.trigger_name`, `.current_url`,
`.prompt`. Use `Depends(require_htmx)` for HTMX-only routes.

### Template Context Providers

```python
from vibetuner.rendering import register_globals
from vibetuner.rendering import register_context_provider

register_globals({"site_title": "My App"})

@register_context_provider
def dynamic_context() -> dict:
    return {"feature_flags": get_flags()}
```

### Runtime Configuration

`from vibetuner.runtime_config import register_config_value, get_config`.
Register with `register_config_value(key=, default=, value_type=,
category=, description=)`. Read with `await get_config("key")`.
Debug UI at `/debug/config`.

### Template Override

Create files in `templates/frontend/` or `templates/email/` to override
defaults.

### Debugging

`uv run vibetuner doctor` — validates project structure, config, env
vars, services, models, templates, deps.

---

## Testing

Fixtures (auto-discovered): `vibetuner_client`, `vibetuner_app`,
`vibetuner_db`, `mock_auth` (`.login()`/`.logout()`), `mock_tasks`,
`override_config`.

```python
@pytest.mark.asyncio
async def test_dashboard(vibetuner_client, mock_auth):
    mock_auth.login(name="Alice", email="alice@example.com")
    resp = await vibetuner_client.get("/dashboard")
    assert resp.status_code == 200
```

Dev server must be running (`just local-all`). Playwright MCP available
at `http://localhost:8000`.

---

## Configuration

**Env vars** (`.env`, not committed): `DATABASE_URL`, `REDIS_URL`,
`SECRET_KEY`, `DEBUG`.

**Settings**: `from vibetuner.config import settings` —
`.environment`, `.debug`, `.resolved_port`, `.expose_url`,
`.mongodb_url`, `.redis_url`, `.workers_available`,
`.project.project_slug`, `.project.project_name`,
`.project.supported_languages`, `.project.default_language`,
`.project.fqdn`.

### Security Headers

CSP with nonce-based scripts enabled by default. The CSP nonce is
auto-injected into all `<script>` tags in HTML responses, so you
don't need to add it manually. Debug mode = report-only. Configure
via `CSP_*` env vars. Avoid inline event handlers (`onclick`
etc.) — use HTMX attributes or `addEventListener`.

### Request ID

Auto-assigned `X-Request-ID` (UUID4), reuses incoming header if
present. Access via `vibetuner.frontend.request_id.get_request_id()`
or `request_id_dependency`.

---

## Localization

```bash
just i18n                    # Full workflow
just new-locale LANG         # New language
```

Templates: `{% trans %}Welcome{% endtrans %}`.
Python: `from starlette_babel import gettext_lazy as _`.

---

## Code Style

**Python**: Type hints always, async/await for DB ops,
**run `ruff format .` after changes**, 88 char lines.

**Frontend**: HTMX for dynamics, Tailwind classes, DaisyUI components,
extend `base/skeleton.html.jinja`.

**Tailwind 4**: Use utility classes and arbitrary values
(`text-[13px]`, `bg-[#1DB954]`). Define tokens in `config.css`
`@theme {}`. No inline styles.

---

## Ad-hoc Database Operations

Uses `pymongo` (not `motor`). Use `AsyncMongoClient` and
`get_pymongo_collection()`. Existing documents may have `None` for
fields with Pydantic defaults — include `None` in filters.

---

## Important Rules

1. Never modify `vibetuner` package
2. All your code goes in `src/app/`
3. Always run `ruff format .` after Python changes
4. Use `uv` exclusively for Python
5. Override, don't modify core templates
6. Never inspect `bundle.css`/`bundle.js` — edit `config.css`/`config.js`
7. Configure in `tune.py` — don't rely on auto-discovery
