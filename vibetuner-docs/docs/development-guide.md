# Development Guide

Daily development workflow for Vibetuner projects.

!!! note "Package name convention"
    In all examples, `app` refers to your project's Python package (the directory under `src/`).
    The actual name depends on your project slug (e.g., `src/myproject/` for a project named
    "myproject").

## Development Environment

Vibetuner supports two development modes:

### Docker Development (Recommended)

Run everything in containers with hot reload:

```bash
just dev
```

This starts:

- Database (MongoDB or SQL, if configured)
- Redis (if background jobs enabled)
- FastAPI application with auto-reload
- Frontend asset compilation with watch mode (tailwind + bundler watchers
  spawned inside the app container)

Changes to Python code, templates, and assets automatically reload — the
container syncs from the host via `docker compose up --watch`, granian
restarts workers on Python edits, and bun watchers rebuild
`bundle.css`/`bundle.js` on template/JS edits.

The host port is **derived deterministically from the project directory**
(in the 14000–17999 band), so two scaffolded projects can run `just dev`
side-by-side without colliding on `8000`. The mapped port is printed when
the container starts; `docker compose -f compose.dev.yml ps` also shows it.

> **Tailwind v4 quirk:** edits to `config.css` itself don't trigger a
> rebuild — restart `just dev` after changing it. Edits to templates and
> other `@source`-watched directories rebuild without restart. See
> [tailwindlabs/tailwindcss#14726](https://github.com/tailwindlabs/tailwindcss/issues/14726).

### Local Development

Run services locally without Docker:

```bash
just install-deps            # Run once after cloning or updating lockfiles
just local-all               # Runs server + assets with auto-port (recommended)
just local-all-with-worker   # Includes background worker (requires Redis)
```

A database (MongoDB or SQL) is required if using database features. Redis is only required if
background jobs are enabled.

`local-all` also derives a deterministic port (in the 10000–13999 band for
the frontend, 20000–23999 for the worker UI), distinct from `just dev`'s
14000–17999 docker band. So `just local-all` (running against your shared
prod-style services) and `just dev` (running fully containerized against
local mongo/redis) can be alive simultaneously without port conflict.

## Justfile Commands Reference

All project management tasks use `just` (command runner). Run `just` without arguments to see all
available commands.

### Development

```bash
just local-all               # Local dev: server + assets with auto-port (recommended)
just local-all-with-worker   # Local dev with background worker (requires Redis)
just dev                     # Docker development with hot reload
just local-dev PORT=8000     # Local server only (run bun dev separately)
just worker-dev              # Background worker only
```

### Dependencies

```bash
just install-deps            # Install from lockfiles
just update-repo-deps        # Update root scaffolding dependencies
just update-and-commit-repo-deps  # Update deps and commit changes
uv add package-name          # Add Python package
bun add package-name         # Add JavaScript package
```

### Code Formatting

```bash
just format                  # Format ALL code (Python, Jinja, TOML, YAML)
just format-py               # Format Python with ruff
just format-jinja            # Format Jinja templates with djlint
just format-toml             # Format TOML files with taplo
just format-yaml             # Format YAML files with dprint
```

**IMPORTANT**: Always run `ruff format .` or `just format-py` after Python changes.

### Code Linting

```bash
just lint                    # Lint ALL code
just lint-py                 # Lint Python with ruff
just lint-jinja              # Lint Jinja templates with djlint
just lint-md                 # Lint markdown files
just lint-toml               # Lint TOML files with taplo
just lint-yaml               # Lint YAML files with dprint
just type-check              # Type check Python with ty
```

### Localization (i18n)

```bash
just i18n                    # Full workflow: extract, update, compile
just extract-translations    # Extract translatable strings
just update-locale-files     # Update existing .po files
just compile-locales         # Compile .po to .mo files
just new-locale LANG         # Create new language (e.g., just new-locale es)
just dump-untranslated DIR   # Export untranslated strings
```

### CI/CD & Deployment

```bash
just build-dev               # Build development Docker image
just test-build-prod         # Test production build locally
just build-prod              # Build production image (requires clean tagged commit)
just release                 # Build and release production image
just deploy-latest HOST      # Deploy to remote host
```

### Scaffolding Updates

```bash
just update-scaffolding      # Update project to latest vibetuner template
just deps-scaffolding        # Update deps + scaffolding on the current branch (no PR)
just deps-scaffolding-pr     # Update deps + scaffolding in a worktree and open a PR
```

## Common Tasks

### Adding New Routes

Create a new file in `src/app/frontend/routes/`. Routes are **automatically discovered**, no
registration needed:

```python
# src/app/frontend/routes/blog.py
from fastapi import APIRouter

router = APIRouter(prefix="/blog", tags=["blog"])

@router.get("/")
async def list_posts():
    return {"posts": []}
```

The framework finds any `router` variable in route files and registers it automatically.

#### `@render` Decorator

For simple routes, use `@render()` to eliminate `render_template()` boilerplate.
Return a dict and the decorator handles rendering:

```python
from vibetuner import render

@router.get("/dashboard")
@render("dashboard.html.jinja")
async def dashboard(request: Request, user=Depends(get_current_user)) -> dict:
    return {"user": user}
```

The decorator auto-extracts `request` from route parameters. If the route returns a
`Response` object (e.g. `RedirectResponse`) instead of a dict, it passes through
unchanged — this is the escape hatch for conditional logic:

```python
@router.get("/items/{id}")
@render("items/detail.html.jinja")
async def item_detail(request: Request, id: str) -> dict:
    item = await Item.get(id)
    if not item:
        return RedirectResponse("/items")  # Passed through as-is
    return {"item": item}
```

#### Streaming Large Pages

For large pages (dashboards, data tables), use `render_template_stream()` to send
HTML chunks as the template renders. The browser can start painting the `<head>` and
initial layout before the full page is ready:

```python
from vibetuner import render_template_stream

@router.get("/dashboard")
async def dashboard(request: Request):
    data = await get_dashboard_data()
    return render_template_stream("dashboard.html.jinja", request, {"data": data})
```

Context merging works identically to `render_template()`. Best suited for full page
loads — HTMX partials are typically small and don't benefit from streaming.

### Adding Database Models

Create models in `src/app/models/`. Models are **automatically discovered** and initialized.

#### MongoDB (Beanie ODM)

```python
# src/app/models/post.py
from beanie import Document
from pydantic import Field

class Post(Document):
    title: str
    content: str
    published: bool = Field(default=False)

    class Settings:
        name = "posts"
```

No `__init__.py` registration needed. The framework auto-discovers Beanie Documents.

#### SQL (SQLModel)

```python
# src/app/models/post.py
from sqlmodel import SQLModel, Field

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    published: bool = Field(default=False)
```

Register SQL models explicitly in `tune.py`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.models.post import Post

app = VibetunerApp(
    sql_models=[Post],
)
```

For SQL databases, create tables with: `vibetuner db create-schema`

!!! tip "MongoDB is optional"
    Projects that only use SQLModel/Postgres do not need `MONGODB_URL`.
    The framework silently skips MongoDB initialization when the URL is not set.

#### Soft Delete

Instead of permanently removing documents, soft delete marks them with a `deleted_at` timestamp.
Soft-deleted documents stay in the database but are automatically excluded from queries.

Use `DocumentWithSoftDelete` instead of `Document` as your base class:

```python
# src/app/models/post.py
from vibetuner.models import DocumentWithSoftDelete
from vibetuner.models.mixins import TimeStampMixin

class Post(DocumentWithSoftDelete, TimeStampMixin):
    title: str
    content: str

    class Settings:
        name = "posts"
```

This adds an optional `deleted_at` field to your document automatically.

**Deleting and querying:**

```python
post = await Post.find_one(Post.title == "Draft")

await post.delete()          # sets deleted_at, document stays in DB
post.is_deleted()            # True

await Post.find_all().to_list()          # excludes soft-deleted documents
await Post.find_many_in_all().to_list()  # includes soft-deleted documents

await post.hard_delete()     # permanently removes the document
```

`find()`, `find_one()`, and `get()` all automatically filter out soft-deleted documents.
Use `find_many_in_all()` when you need to access them (e.g., admin views, audit logs).

**Restoring a soft-deleted document:**

```python
post.deleted_at = None
await post.save()
```

**CRUD factory:** The `DELETE` endpoint automatically performs a soft delete for models
that use `DocumentWithSoftDelete`. No configuration needed.

#### Encrypted Fields

Encrypt sensitive fields at rest using `EncryptedFieldsMixin` and the
`EncryptedStr` type. Fields are transparently encrypted before database
writes and decrypted on load:

```python
from beanie import Document
from pydantic import Field
from vibetuner.models.mixins import EncryptedFieldsMixin, EncryptedStr

class ApiCredential(Document, EncryptedFieldsMixin):
    provider: str
    api_key: EncryptedStr = Field(..., description="Encrypted API key")
    token: EncryptedStr | None = Field(default=None)

    class Settings:
        name = "api_credentials"
```

```python
# Usage — encryption/decryption is automatic
cred = ApiCredential(provider="stripe", api_key="sk_live_xxx")
await cred.insert()         # api_key is encrypted before write

loaded = await ApiCredential.get(cred.id)
print(loaded.api_key)       # "sk_live_xxx" — decrypted on load
```

Encryption requires the `FIELD_ENCRYPTION_KEY` environment variable
(a Fernet key). When the key is not set, fields are stored as plaintext.
Use `vibetuner crypto set-key` to generate and configure a key, and
`vibetuner crypto rotate-key` to rotate it. See the
[CLI Reference](cli-reference.md#vibetuner-crypto) for details.

### Creating Templates

Add templates in `templates/frontend/`:

```html
<!-- templates/frontend/blog/list.html.jinja -->
{% extends "base/skeleton.html.jinja" %}
{% block content %}
    <div class="container mx-auto">
        <h1 class="text-3xl font-bold">Blog Posts</h1>
        <div class="grid gap-4">
            {% for post in posts %}
                <article class="card">
                    <h2>{{ post.title }}</h2>
                    <div>{{ post.content }}</div>
                </article>
            {% endfor %}
        </div>
    </div>
{% endblock content %}
```

#### Template Path Convention

The template search path already includes `templates/frontend/`, so when calling
`render_template()` use paths **relative to that directory**:

```python
# Correct - path relative to templates/frontend/
render_template("blog/list.html.jinja", request)
render_template("admin/dashboard.html.jinja", request)

# Wrong - "frontend/" prefix is redundant and causes TemplateNotFound
render_template("frontend/blog/list.html.jinja", request)  # TemplateNotFound!
```

The same convention applies to `{% extends %}` and `{% include %}` inside templates:

```html
{% extends "base/skeleton.html.jinja" %}          {# correct #}
{% extends "frontend/base/skeleton.html.jinja" %} {# wrong #}
```

#### Skeleton Extension Points

The shipped `base/skeleton.html.jinja` exposes blocks and context variables so
projects can slot in customisations without copying the whole skeleton.
Extending it is preferable to overriding it: upstream changes (CSP nonce,
theming, etc.) flow through automatically.

**Blocks** (override in any child template):

| Block | Position | Use for |
| --- | --- | --- |
| `extra_head_links` | After `<title>`, before `bundle.css` | `<link rel="alternate">` feeds, RSS, custom meta tags |
| `extra_scripts` | After the bundled `<script>` (and optional umami) | Per-app scripts that don't replace `bundle.js` |
| `before_main` | Inside `<body>`, before `block body` | Dev banners, sticky overlays |
| `after_main` | Inside `<body>`, after `block body` | Persistent mini-players, floating toolbars |

Existing blocks already there: `title`, `head`, `scripts`, `start_of_body`,
`header`, `body`, `content`, `footer`, `end_of_body`.

**Context variables** (set via `register_globals`, a context provider, or
per-render `ctx`):

| Variable | Type | Default | Effect |
| --- | --- | --- | --- |
| `color_scheme` | `str` | `"light"` | Sets `<meta name="color-scheme">` content |
| `canonical_url` | `str \| None` | `None` | When set, renders `<link rel="canonical" href="…">` |
| `font_preloads` | `list[dict]` | `[]` | Each entry renders `<link rel="preload" as="font" href="…" type="…" [crossorigin="…"]>` |

```python
# tune.py
from vibetuner import register_globals

register_globals({"color_scheme": "dark"})  # whole site is dark
```

```python
# Per-page canonical URL
return render_template(
    "blog/post.html.jinja",
    request,
    {"canonical_url": str(request.url_for("blog_post", slug=post.slug))},
)
```

```python
# Self-hosted brand fonts (preload-scanner picks these up before bundle.css)
register_globals({
    "font_preloads": [
        {"href": "/static/fonts/brand.woff2", "type": "font/woff2", "crossorigin": "anonymous"},
    ],
})
```

```html
<!-- templates/frontend/base/skeleton.html.jinja override -->
{% extends "base/skeleton.html.jinja" %}

{% block extra_head_links %}
    <link rel="alternate" type="application/rss+xml"
          title="My App" href="{{ url_for('rss').path }}" />
{% endblock extra_head_links %}

{% block after_main %}
    {# Persistent player survives HTMX boost swaps #}
    {% include "components/player.html.jinja" %}
{% endblock after_main %}
```

If you do need to override the whole skeleton (e.g. to wrap the body in an
HTMX-boost container, change the `<html>` attributes, or add markup before
`<head>`), prefer the smallest possible override and keep the upstream
blocks intact so future framework changes still apply.

### Built-in Template Globals

Vibetuner provides these variables in every template automatically:

| Variable | Type | Value |
|----------|------|-------|
| `now` | `datetime` | `datetime.now(timezone.utc)` — timezone-aware UTC datetime |
| `today` | `str` | `date.today().isoformat()` — ISO date string (e.g., `"2026-04-07"`) |

```html
<p>Page rendered at {{ now | format_datetime }}</p>
<p>Today is {{ today }}</p>
<footer>&copy; {{ now.year }} My Company</footer>
```

These are re-evaluated on every render, so `now` reflects the current
request time. For custom globals, see
[Template Context Providers](#template-context-providers).

### Built-in Template Filters

Vibetuner provides several built-in template filters for common formatting needs:

| Filter | Usage | Output |
|--------|-------|--------|
| `timeago` | `{{ dt \| timeago }}` | "5 minutes ago" |
| `timeago(short=True)` | `{{ dt \| timeago(short=True) }}` | "5m ago" |
| `format_date` | `{{ dt \| format_date }}` | "January 15, 2025" |
| `format_datetime` | `{{ dt \| format_datetime }}` | "January 15, 2025 at 2:30 PM" |
| `format_duration` / `duration` | `{{ seconds \| duration }}` | "5 min" or "30 sec" |

#### timeago Filter

The `timeago` filter converts a datetime to a human-readable relative time string:

```html
<span>Created {{ post.created_at | timeago }}</span>
<!-- Output: "5 minutes ago", "yesterday", "3 months ago", etc. -->

<!-- Short format for compact displays -->
<span>{{ post.created_at | timeago(short=True) }}</span>
<!-- Output: "5m ago", "1d ago", "3mo ago", etc. -->
```

Short format outputs:

| Time Range | Short Format |
|------------|--------------|
| < 60 seconds | "just now" |
| < 60 minutes | "Xm ago" |
| < 24 hours | "Xh ago" |
| < 7 days | "Xd ago" |
| < 30 days | "Xw ago" |
| < 365 days | "Xmo ago" |
| < 4 years | "Xy ago" |
| >= 4 years | "MMM DD, YYYY" |

### Adding Custom Template Filters

Register custom Jinja2 filters via the `template_filters` dict in `VibetunerApp`:

```python
# src/app/frontend/templates.py
def uppercase(value):
    """Convert value to uppercase"""
    return str(value).upper()

def format_money(value):
    """Format value as USD currency"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.frontend.templates import uppercase, format_money

app = VibetunerApp(
    template_filters={
        "uppercase": uppercase,
        "money": format_money,
    },
)
```

Use in templates:

```html
<h1>{{ user.name | uppercase }}</h1>
<p>Price: {{ product.price | money }}</p>
```

### Adding Background Jobs

If you enabled background jobs, create tasks in `src/app/tasks/`. Task modules are
**automatically discovered**:

```python
# src/app/tasks/emails.py
from vibetuner.tasks.worker import get_worker
from vibetuner.models import UserModel
from vibetuner.services.email import EmailService

worker = get_worker()

@worker.task()
async def send_welcome_email(user_id: str):
    user = await UserModel.get(user_id)
    if user:
        email_service = EmailService()
        await email_service.send_email(
            to_address=user.email,
            subject="Welcome!",
            html_body="<h1>Welcome!</h1>",
            text_body="Welcome!",
        )
    return {"status": "sent"}
```

Queue jobs from your routes:

```python
from app.tasks.emails import send_welcome_email

@router.post("/signup")
async def signup(email: str):
    # Create user
    user = await create_user(email)

    # Queue background task
    task = await send_welcome_email.enqueue(str(user.id))

    return {"message": "Welcome email queued", "task_id": task.id}
```

### Styling with Tailwind

Vibetuner uses Tailwind CSS + DaisyUI. Edit `assets/config.css` for custom styles:

```css
/* assets/config.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
.btn-custom {
@apply btn btn-primary rounded-full;
}
```

The build process automatically compiles to `assets/statics/css/bundle.css`.

### Brand Configuration

DaisyUI tokens and CSS variables cover everything that renders inside the
page, but a few brand surfaces are read before any CSS runs (favicon meta
tags, the PWA manifest) or in clients that ignore CSS variables (email
clients). `BrandSettings` is an app-level pydantic-settings surface that
drives those specific surfaces:

```bash
# .env (all three are optional; defaults shown)
BRAND_PRIMARY_COLOR=#5b2333
BRAND_BROWSER_THEME_COLOR=#ffffff
BRAND_EMAIL_BUTTON_COLOR=  # falls back to BRAND_PRIMARY_COLOR when unset
```

- `BRAND_PRIMARY_COLOR` — Safari pinned-tab `mask-icon` color, Windows
  tile color (`browserconfig.xml`), and the magic-link email button when
  no override is set.
- `BRAND_BROWSER_THEME_COLOR` — mobile browser chrome
  (`<meta name="theme-color">`) and the PWA manifest's `theme_color` /
  `background_color`.
- `BRAND_EMAIL_BUTTON_COLOR` — override slot for the magic-link email
  button when it needs to differ from the primary brand color.

Inputs accept any pydantic `Color` form (named, `rgb()`, hex short or
long); values canonicalise to long-form `#rrggbb` lowercase before
rendering.

```python
from vibetuner.config import settings

settings.brand.primary_color        # HexColor("#5b2333")
settings.brand.browser_theme_color  # HexColor("#ffffff")
settings.brand.email_button         # email_button_color or primary_color
```

`settings.brand` is exposed in every Jinja render via the shipped
`_brand_context` provider, so templates read `{{ brand.primary_color }}`
without wiring anything up. `BrandSettings` is deliberately app-level
(favicon assets are static files served before tenant resolution; the
email service does not see request context). For per-tenant in-page
colors, use `TenantTheme`.

### Security Headers and CSP Nonce

Vibetuner includes `SecurityHeadersMiddleware` that sets security headers
(X-Content-Type-Options, X-Frame-Options, Referrer-Policy, etc.) and
generates a Content Security Policy with a unique nonce per request.

**Script tags** get the nonce auto-injected by the middleware. Do not add
`nonce=` attributes to `<script>` tags manually:

```html
<!-- Correct — nonce is added automatically by middleware -->
<script src="/static/app.js"></script>

<!-- Wrong — manual nonce causes double-injection issues -->
<script nonce="{{ csp_nonce }}" src="/static/app.js"></script>
```

**Style tags and other elements** that need the nonce must use the
`{{ csp_nonce }}` template variable (available in all templates):

```html
<style nonce="{{ csp_nonce }}">
    .highlight { color: red; }
</style>
```

CSP is fully enforced in both production and debug mode by default, so
violations break the page locally and are caught before they ship. To
fall back to the legacy soft mode (where debug emits
`Content-Security-Policy-Report-Only`), set
`CSP_ENFORCE_CSP_IN_DEBUG=false`.

Configure extra allowed sources via environment variables:

| Variable | Description |
|----------|-------------|
| `CSP_EXTRA_SCRIPT_SRC` | Additional script sources |
| `CSP_EXTRA_STYLE_SRC` | Additional style sources |
| `CSP_EXTRA_IMG_SRC` | Additional image sources |
| `CSP_EXTRA_CONNECT_SRC` | Additional connect sources |
| `CSP_EXTRA_FONT_SRC` | Additional font sources |
| `CSP_EXTRA_MEDIA_SRC` | Additional media sources |
| `CSP_ENFORCE_CSP_IN_DEBUG` | Enforce CSP in debug mode (default: `true`) |

### htmx Nonce Protection (opt-in)

htmx 4.0.0-beta3 ships an `hx-nonce` extension that gates htmx attribute
processing behind the page CSP nonce. Elements without a matching
`hx-nonce` attribute are stripped at init time, providing a
defence-in-depth layer against HTML injection attacks: even if an
attacker manages to inject HTML, the browser will not honour any
`hx-get`/`hx-post`/etc. attributes on injected elements.

The framework's templates already stamp `hx-nonce="{{ csp_nonce }}"` on
their htmx-bearing elements, so the extension is safe to enable from a
fresh project as soon as you mirror the pattern in your own templates.

**To enable:**

1. Add the import to your `config.js` custom imports section:

    ```javascript
    // Add your custom imports below:
    import "./node_modules/htmx.org/dist/ext/hx-nonce.js";
    ```

2. Add `hx-nonce="{{ csp_nonce }}"` to every element in your templates
   that uses any `hx-*` attribute:

    ```html
    <button hx-post="/save"
            hx-target="#main-content"
            hx-nonce="{{ csp_nonce }}">Save</button>
    ```

The extension reads the page nonce from the first `<script nonce>`
element on the page. Vibetuner's `SecurityHeadersMiddleware` already
stamps that nonce on your bundle script, so no extra wiring is required.

**Trusted Types (further hardening):** Once the extension is enabled
you can also tell the browser to refuse non-htmx HTML sinks by adding
`require-trusted-types-for 'script'; trusted-types htmx` to your CSP.
Configure this via `CSP_EXTRA_*` if you need to merge it with other
directives, or extend `SecurityHeadersMiddleware` directly.

**Safe eval:** vibetuner's CSP does not include `'unsafe-eval'`, so any
htmx feature that requires `eval` (e.g. `hx-vals` with the `js:` prefix,
`hx-on:` handlers that reference globals) will be blocked by default.
If you use those features, set `safeEval:true` in your htmx config —
the extension replaces htmx's `new Function()` eval with nonce-based
script injection so the features work without `unsafe-eval`.

## Working with HTMX

Vibetuner uses HTMX for interactive features without JavaScript:

```html
<!-- Load more posts -->
<button hx-get="/blog?page=2"
        hx-target="#posts"
        hx-swap="beforeend"
        class="btn btn-primary">Load More</button>
<div id="posts">
    <!-- Posts will be appended here -->
</div>
```

Server endpoint:

```python
@router.get("/blog")
async def list_posts(page: int = 1):
    posts = await Post.find().skip((page - 1) * 10).limit(10).to_list()
    return templates.TemplateResponse("blog/posts.html.jinja", {
        "posts": posts
    })
```

### HTMX Request Detection

Every request has `request.state.htmx` available (provided by the `starlette-htmx`
middleware). Use it to serve different responses for HTMX vs regular requests:

```python
from fastapi import Request
from starlette.responses import HTMLResponse
from vibetuner import render_template, render_template_string

@router.get("/items")
async def list_items(request: Request):
    items = await Item.find_all().to_list()
    ctx = {"items": items}

    if request.state.htmx:
        # HTMX request — return just the partial
        html = render_template_string("items/_list.html.jinja", request, ctx)
        return HTMLResponse(html)

    # Regular request — return the full page
    return render_template("items/list.html.jinja", request, ctx)
```

**Available properties on `request.state.htmx`:**

| Property | Description |
|----------|-------------|
| `bool(request.state.htmx)` | `True` if this is an HTMX request |
| `.boosted` | `True` if request came via `hx-boost` |
| `.target` | ID of the target element (`hx-target`) |
| `.trigger` | ID of the element that triggered the request |
| `.trigger_name` | Name attribute of the triggering element |
| `.current_url` | Browser's current URL when request was made |
| `.prompt` | User response from `hx-prompt` |

### HTMX Response Headers

Helper functions for setting HTMX response headers. Import from `vibetuner.htmx`:

```python
from vibetuner.htmx import hx_redirect, hx_location, hx_trigger

# Full-reload redirect (when <head> or scripts differ)
return hx_redirect("/items/123")

# HTMX-style navigation without full reload
return hx_location("/items", target="#main", swap="innerHTML")

# Trigger client-side events after swap
response = render_template("items/created.html.jinja", request, ctx)
hx_trigger(response, "itemCreated", {"id": str(item.id)})
return response
```

Available helpers: `hx_redirect`, `hx_location`, `hx_trigger`,
`hx_trigger_after_settle`, `hx_trigger_after_swap`, `hx_push_url`,
`hx_replace_url`, `hx_reswap`, `hx_retarget`, `hx_refresh`.

JSON serialization is handled internally — you never need to call `json.dumps()`.

### Response Caching (Server-Side)

Use the `@cache` decorator to cache route responses in Redis with a configurable TTL.
This is ideal for expensive queries, aggregation endpoints, or rendered pages that
don't change on every request:

```python
from vibetuner.cache import cache

@router.get("/api/stats")
@cache(expire=60)  # cache for 60 seconds
async def get_stats(request: Request):
    return {"users": await count_users()}
```

The decorator uses vibetuner's existing Redis connection — no extra setup required
if you already have `REDIS_URL` configured.

**Key features:**

- Cache key derived from route path + sorted query parameters
- Respects `Cache-Control: no-cache` request header (bypasses cache)
- Works with JSON, HTML, and dict responses
- **Disabled by default in debug mode** — pass `force_caching=True` to override
- If Redis is not configured or unavailable, the decorator is a transparent no-op

**Request-dependent cache keys with `vary_on`:**

Use `vary_on` to cache different responses for different users, tenants, or
any other request-derived dimension:

```python
# Per-user cache — each user gets their own cached dashboard
@router.get("/dashboard")
@cache(expire=120, vary_on=lambda r: str(r.state.user.id))
async def dashboard(request: Request):
    return await render_dashboard(request)

# Per-tenant cache
@router.get("/reports")
@cache(expire=300, vary_on=lambda r: r.state.tenant_id)
async def reports(request: Request):
    return await generate_reports(request)

# Vary by header
@router.get("/api/data")
@cache(expire=60, vary_on=lambda r: r.headers.get("x-tenant", ""))
async def data(request: Request):
    return await fetch_data(request)
```

`vary_on` accepts a callable with signature `(Request) -> str`. The
returned string is included in the cache key, so different values produce
independent cache entries. When `None` (the default), all requests to the
same path and query share one cache entry.

**Cache invalidation:**

```python
from vibetuner.cache import invalidate, invalidate_pattern

# Invalidate a specific path
await invalidate("/api/stats")

# Invalidate a specific query variant
await invalidate("/api/stats", query_params="page=1")

# Invalidate all matching paths (uses Redis SCAN)
await invalidate_pattern("/api/*")
```

### Cache Control Headers (Browser-Side)

Use the `@cache_control` decorator to set `Cache-Control` HTTP headers declaratively
instead of manually manipulating response headers:

```python
from vibetuner.decorators import cache_control

@router.get("/static-page")
@cache_control(max_age=300, public=True)
async def static_page(request: Request):
    return render_template("static_page.html.jinja", request)
```

Supported directives: `public`, `private`, `no_cache`, `no_store`, `max_age`,
`s_maxage`, `must_revalidate`, `stale_while_revalidate`, `immutable`.

You can combine both decorators — `@cache` for server-side Redis caching and
`@cache_control` for browser-side HTTP caching:

```python
@router.get("/api/stats")
@cache(expire=60)
@cache_control(max_age=30, public=True)
async def get_stats(request: Request):
    return {"users": await count_users()}
```

### Block Rendering for HTMX Partials

Use `render_template_block()` to render a single `{% block %}` from a template,
enabling one template to serve both full-page and HTMX partial responses:

```html
<!-- templates/frontend/items/list.html.jinja -->
{% extends "base/skeleton.html.jinja" %}
{% block body %}
<div id="items-container">
    {% block items_list %}
    {% for item in items %}
        <div class="item">{{ item.name }}</div>
    {% endfor %}
    {% endblock items_list %}
</div>
{% endblock body %}
```

```python
from vibetuner import render_template, render_template_block

@router.get("/items")
async def list_items(request: Request):
    items = await Item.find_all().to_list()
    ctx = {"items": items}

    if request.state.htmx:
        return render_template_block(
            "items/list.html.jinja", "items_list", request, ctx
        )

    return render_template("items/list.html.jinja", request, ctx)
```

For HTMX [out-of-band swaps](https://htmx.org/attributes/hx-swap-oob/) that update
multiple page regions in one response, use `render_template_blocks()` (plural):

```python
from vibetuner import render_template_blocks

@router.post("/items")
async def create_item(request: Request):
    item = await Item.insert(...)
    items = await Item.find_all().to_list()
    ctx = {"items": items, "item_count": len(items)}

    return render_template_blocks(
        "items/list.html.jinja",
        ["items_list", "notification_badge"],
        request, ctx,
    )
```

### HTMX-Only Routes

Use the `require_htmx` dependency to reject non-HTMX requests with a 400 error:

```python
from fastapi import Depends
from vibetuner.frontend.deps import require_htmx

@router.post("/items/create", dependencies=[Depends(require_htmx)])
async def create_item(request: Request):
    # Only reachable via HTMX — non-HTMX requests get 400
    ...
```

### Using `hx-boost`

For links and forms that should use HTMX navigation without writing custom
`hx-get`/`hx-post` attributes, use `hx-boost="true"` on a parent element. Boosted
links and forms swap the `<body>` content and update the URL without a full page
reload:

```html
<nav hx-boost="true">
    <a href="/dashboard">Dashboard</a>
    <a href="/settings">Settings</a>
</nav>
```

Boosted requests set `request.state.htmx.boosted = True`. Since boosted requests
expect a full page response (they swap the entire body), you typically don't need
to branch on `request.state.htmx` for boosted routes.

## Internationalization

### Extracting Translations

After adding translatable strings:

```bash
just extract-translations
```

This scans your code and templates for `{% trans %}` blocks and `gettext()` calls.

### Adding New Languages

```bash
just new-locale es  # Spanish
just new-locale fr  # French
```

### Updating Translations

Edit `.po` files in `translations/`:

```po
# translations/es/LC_MESSAGES/messages.po
msgid "Welcome"
msgstr "Bienvenido"
```

Compile translations:

```bash
just compile-locales
```

### Using in Templates

```html
{% trans %}Welcome to {{ app_name }}{% endtrans %}
```

### Using in Python

```python
from starlette_babel import gettext as _
message = _("Welcome to {app}", app=app_name)
```

### Template Context Variables for i18n

The following language-related variables are available in templates:

| Variable | Type | Description |
|----------|------|-------------|
| `default_language` | `str` | Default language code (e.g., "en") |
| `supported_languages` | `set[str]` | Set of supported language codes |
| `locale_names` | `dict[str, str]` | Language codes to native display names |
| `language` | `str` | The active language for the current request |

A `language_picker()` Jinja global is also available — see below.

#### When to use which

`locale_names` and `language_picker()` overlap but solve different problems:

- **`locale_names`** — locale-independent map of native names, frozen at app startup
  and sorted by name. Use it when every language must always render in its own script
  (e.g. a footer that reads "English / Català / Español" regardless of the visitor's
  language).
- **`language_picker()`** — `[{code, name}]` list with names rendered in the current
  request locale (or an explicit `display_locale`). Use it for switchers that should
  render themselves in the user's active language.

If you want native names but prefer a single source of truth, call
`language_picker(code)` once per language instead of reading `locale_names`.

#### Using `language_picker()` for Locale-Aware Switchers

`language_picker()` is a Jinja global (also importable as
`vibetuner.i18n.language_picker`) that returns a sorted list of
`{code, name}` entries with names rendered in the **current request's
locale**. Browsing in Spanish gives "inglés / español / catalán";
browsing in Catalan gives "anglès / espanyol / català".

```html
<select name="language">
    {% for entry in language_picker() %}
        <option value="{{ entry.code }}"
                {% if entry.code == language %}selected{% endif %}>
            {{ entry.name }}
        </option>
    {% endfor %}
</select>
```

Pass an explicit `display_locale` to render names in a specific language
regardless of the request locale: `{% for e in language_picker("es") %}`.

#### Using `locale_names` for native names

`locale_names` is locale-independent — each language is shown in its own native name
(e.g. `{"ca": "Català", "en": "English", "es": "Español"}`). Use this when you want a
consistent display regardless of the user's current language.

### SEO-Friendly Language URLs

Vibetuner supports path-prefix language routing for SEO-friendly URLs (e.g., `/ca/privacy`,
`/es/about`).

#### How It Works

The `LangPrefixMiddleware` handles path-prefix language routing:

| URL | Behavior |
|-----|----------|
| `/ca/dashboard` | Strips prefix → `/dashboard`, sets lang=ca |
| `/dashboard` (anonymous) | Serves directly using detected/default language |
| `/dashboard` (authenticated) | 301 redirects to `/{user_lang}/dashboard` |
| `/xx/dashboard` (invalid) | Returns 404 Not Found |
| `/ca` | Redirects to `/ca/` |
| `/static/...` | Bypassed, serves static file directly |

#### Language Detection Priority

Languages are detected in this order (first match wins):

1. **Custom resolvers** registered via
   [`register_locale_resolver`](#custom-locale-resolvers-register_locale_resolver)
2. Query parameter (`?l=es`)
3. URL path prefix (`/ca/...`)
4. User preference (from session, for authenticated users)
5. Cookie (`language` cookie)
6. Accept-Language header (browser preference)
7. Default language

#### Custom Locale Resolvers (`register_locale_resolver`)

For per-tenant or domain-specific locale rules, register a custom resolver at
startup. Resolvers run **before** all built-in selectors and the first one to
return a non-`None` value wins. Within the registered group, resolvers are
ordered by `priority` ascending (lower runs first).

```python
from vibetuner.i18n import register_locale_resolver

def tenant_locale(conn):
    tenant = getattr(conn.scope.get("state", {}), "tenant", None)
    return tenant.language if tenant else None

register_locale_resolver(tenant_locale)
```

Resolvers must be synchronous (do any I/O upstream in middleware). If a
resolver raises, the exception is logged and the chain falls through to the
next resolver — a bad lookup never produces a 500.

#### Forcing a Language Mid-Request (`set_request_language`)

To change the active language partway through a request (e.g. right after a
session login), use `set_request_language`. It updates both the Babel context
(drives `{% trans %}`) and `request.state.language` (drives `<html lang>` and
the `Content-Language` header) in one call so they stay in sync.

```python
from vibetuner.i18n import set_request_language

set_request_language(request, user.preferred_language)
```

The code is normalized to lowercase and validated; an invalid code raises
`ValueError`.

#### Programmatic Language Picker (`language_picker`)

When you need the picker output outside a template (e.g. JSON endpoint, email
rendering), call `language_picker` directly. By default the names are
rendered in the current request's locale.

```python
from vibetuner.i18n import language_picker

choices = language_picker()  # display in current locale
es_choices = language_picker(display_locale="es")  # always in Spanish
```

#### Redirect Behavior

Localized routes follow these rules:

- **Anonymous users**: Served at unprefixed URL using detected/default language
- **Authenticated users**: 301 permanent redirect to `/{lang}/path`

This approach optimizes for SEO: search engines crawl the unprefixed URL (which serves the
default language) and discover language variants via `hreflang` tags, while authenticated
users get a personalized, bookmarkable URL.

#### Using LocalizedRouter (Recommended)

Use `LocalizedRouter` to control localization at the router level. All routes automatically
handle language prefix redirects:

```python
from fastapi import Request
from vibetuner.frontend import LocalizedRouter
from vibetuner import render_template

# All routes in this router are localized
legal_router = LocalizedRouter(prefix="/legal", localized=True)

@legal_router.get("/privacy")
async def privacy(request: Request):
    return render_template("legal/privacy.html.jinja", request)
    # Anonymous: served at /legal/privacy
    # Authenticated: redirected to /{lang}/legal/privacy

# All routes in this router are non-localized (API endpoints)
api_router = LocalizedRouter(prefix="/api", localized=False)

@api_router.get("/users")
async def users():
    return {"users": []}  # Always at /api/users, no redirects
```

#### Using @localized Decorator

For individual routes on a regular `APIRouter`, use the `@localized` decorator:

```python
from fastapi import APIRouter, Request
from vibetuner.frontend import localized
from vibetuner import render_template

router = APIRouter()

@router.get("/privacy")
@localized
async def privacy(request: Request):
    return render_template("privacy.html.jinja", request)
```

#### Generating Language URLs in Templates

Two helpers are available for generating language-prefixed URLs:

**`lang_url_for`**: Uses the current request's language:

```html
<a href="{{ lang_url_for(request, 'privacy') }}">Privacy Policy</a>
<!-- Output: /ca/privacy (if current language is Catalan) -->
```

**`url_for_language`**: Specify a target language explicitly (for language switchers):

```html
<a href="{{ url_for_language(request, 'es', 'privacy') }}">Español</a>
<!-- Output: /es/privacy -->
```

#### Adding hreflang Tags for SEO

Use `hreflang_tags` to generate proper hreflang link tags in your page head:

```html
<!-- In your base template <head> -->
{{ hreflang_tags(request, supported_languages, default_language)|safe }}
```

This outputs:

```html
<link rel="alternate" hreflang="ca" href="https://example.com/ca/privacy" />
<link rel="alternate" hreflang="en" href="https://example.com/en/privacy" />
<link rel="alternate" hreflang="es" href="https://example.com/es/privacy" />
<link rel="alternate" hreflang="x-default" href="https://example.com/privacy" />
```

Note: `x-default` points to the unprefixed URL, which serves the default/detected language.

#### Complete Example

Route definition:

```python
# src/app/frontend/routes/legal.py
from fastapi import Request
from vibetuner.frontend import LocalizedRouter
from vibetuner import render_template

router = LocalizedRouter(tags=["legal"], localized=True)

@router.get("/privacy")
async def privacy(request: Request):
    return render_template("legal/privacy.html.jinja", request)

@router.get("/terms")
async def terms(request: Request):
    return render_template("legal/terms.html.jinja", request)
```

Template with hreflang:

```html
<!-- templates/legal/privacy.html.jinja -->
{% extends "base/skeleton.html.jinja" %}

{% block head %}
{{ hreflang_tags(request, supported_languages, default_language)|safe }}
{% endblock head %}

{% block content %}
<h1>{% trans %}Privacy Policy{% endtrans %}</h1>
<!-- Content -->
{% endblock content %}
```

Language switcher using `url_for_language`:

```html
<!-- templates/partials/language_switcher.html.jinja -->
<div class="dropdown">
    {% for code, name in locale_names.items() %}
        <a href="{{ url_for_language(request, code, request.scope.endpoint.__name__) }}"
           {% if code == language %}class="active"{% endif %}>
            {{ name }}
        </a>
    {% endfor %}
</div>
```

## CRUD Factory

Generate complete REST API endpoints from Beanie Document models with a single function call.

### Basic Usage

```python
from vibetuner.crud import create_crud_routes
from app.models.post import Post

post_routes = create_crud_routes(Post, prefix="/posts", tags=["posts"])
```

Include the router in your app via `tune.py`. CRUD routes are JSON API
endpoints, so use `api_routes` to keep them visible in `/docs`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.routes.posts import post_routes

app = VibetunerApp(api_routes=[post_routes])
```

This generates five endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/posts` | List with pagination, filtering, search, sort |
| `POST` | `/posts` | Create a new document |
| `GET` | `/posts/{item_id}` | Read a single document |
| `PATCH` | `/posts/{item_id}` | Partial update |
| `DELETE` | `/posts/{item_id}` | Delete a document |

### Filtering, Searching, and Sorting

```python
post_routes = create_crud_routes(
    Post,
    prefix="/posts",
    sortable_fields=["created_at", "title"],
    filterable_fields=["status", "author_id"],
    searchable_fields=["title", "content"],
    page_size=25,
    max_page_size=100,
)
```

Query examples:

- `GET /posts?status=published` — equality filter
- `GET /posts?search=python` — text search across searchable fields
- `GET /posts?sort=-created_at,title` — sort descending by date, then title
- `GET /posts?offset=20&limit=10` — pagination
- `GET /posts?fields=title,status` — sparse field selection

### Lifecycle Hooks

Attach async callbacks to intercept create, update, and delete operations:

```python
async def check_permissions(doc, data, request):
    if request.state.user.id != str(doc.author_id):
        raise HTTPException(403, "Not your post")
    return data

post_routes = create_crud_routes(
    Post,
    prefix="/posts",
    pre_update=check_permissions,
    post_create=notify_subscribers,
)
```

Available hooks:

| Hook | Signature |
|------|-----------|
| `pre_create` | `async (data, request) -> data` |
| `post_create` | `async (doc, request)` |
| `pre_update` | `async (doc, data, request) -> data` |
| `post_update` | `async (doc, request)` |
| `pre_delete` | `async (doc, request)` |
| `post_delete` | `async (doc, request)` |

### Custom Schemas

Override the auto-generated Pydantic schemas for create/update payloads
or response serialization:

```python
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: str
    title: str
    status: str

post_routes = create_crud_routes(
    Post,
    create_schema=PostCreate,
    response_schema=PostResponse,
)
```

### Restricting Operations

Only generate the endpoints you need:

```python
from vibetuner.crud import create_crud_routes, Operation

# Read-only API
post_routes = create_crud_routes(
    Post,
    operations={Operation.LIST, Operation.READ},
)
```

### Route-Level Dependencies

Apply FastAPI dependencies (e.g., authentication) to all generated routes:

```python
from vibetuner.frontend.auth import require_auth

post_routes = create_crud_routes(
    Post,
    dependencies=[require_auth],
)
```

## SSE / Real-Time Streaming

Server-Sent Events helpers for pushing real-time updates to the browser,
designed for use with HTMX.

### Channel-Based Streaming

Subscribe clients to a named channel and broadcast updates from anywhere:

```python
from vibetuner.sse import sse_endpoint, broadcast

router = APIRouter()

# Endpoint that auto-subscribes to the "notifications" channel
@sse_endpoint("/events/notifications", channel="notifications", router=router)
async def notifications_stream(request: Request):
    pass  # channel kwarg handles the subscription
```

!!! warning "SSE path is relative to router prefix"
    The `path` argument is relative to the router's prefix, just like `@router.get()`.
    If your router has `prefix="/api"`, use `path="/events"` (not `path="/api/events"`)
    to avoid a doubled path like `/api/api/events`.

Broadcast from any route or background task:

```python
from vibetuner.sse import broadcast

@router.post("/posts")
async def create_post(request: Request):
    post = await Post(**data).insert()
    # Push HTML fragment to all subscribers
    await broadcast(
        "notifications",
        "new-post",
        data="<div>New post created!</div>",
    )
    return post
```

### Dynamic Channels

Return a channel name from the decorated function for per-resource streams:

```python
@sse_endpoint("/events/room/{room_id}", router=router)
async def room_stream(request: Request, room_id: str):
    return f"room:{room_id}"  # subscribe to this channel
```

### Template-Rendered Broadcasts

Broadcast rendered Jinja2 partials instead of raw strings:

```python
await broadcast(
    "feed",
    "new-post",
    template="partials/post_card.html.jinja",
    request=request,
    ctx={"post": post},
)
```

### Generator-Based Streaming

For full control, yield events directly from an async generator:

```python
@sse_endpoint("/events/clock", router=router)
async def clock_stream(request: Request):
    while True:
        yield {"event": "tick", "data": datetime.now().isoformat()}
        await asyncio.sleep(5)
```

### HTMX Integration

Connect an SSE endpoint to HTMX using the built-in SSE support:

```html
<div sse-connect="/events/notifications">
    <div sse-swap="new-post" hx-swap="beforeend">
        <!-- new posts appear here -->
    </div>
</div>
```

### Multi-Worker Support

When Redis is configured (`REDIS_URL`), broadcasts are relayed across
all worker processes via Redis pub/sub automatically. No extra setup needed.

## Template Context Providers

Inject variables into every `render_template()` call without passing them
explicitly each time.

### Static Globals

Use `register_globals()` to set values available in all templates:

```python
# src/app/config.py
from vibetuner.rendering import register_globals

register_globals({
    "site_title": "My App",
    "og_image": "/static/og.png",
    "support_email": "help@example.com",
})
```

Values are merged into the template context on every render. Explicit
context passed to `render_template()` takes precedence over globals.

### Dynamic Context Providers

Use `@register_context_provider` for values that are computed at render time:

```python
from vibetuner.rendering import register_context_provider
from vibetuner.runtime_config import get_config

@register_context_provider
def feature_flags() -> dict[str, Any]:
    return {"show_beta_banner": True}

# Also works with parentheses
@register_context_provider()
def analytics_context() -> dict[str, Any]:
    return {"analytics_id": "UA-XXX"}
```

Provider functions must return a `dict[str, Any]`. They run synchronously on
every `render_template()` call. Multiple providers can be registered and their
results are merged.

## Service Dependency Injection

Vibetuner provides FastAPI `Depends()` wrappers for built-in services.

### Available Services

```python
from fastapi import Depends
from vibetuner.services import (
    get_email_service,
    get_blob_service,
    get_runtime_config,
)
```

### Email Service

```python
from vibetuner.services import get_email_service
from vibetuner.services.email import EmailService

@router.post("/contact")
async def contact(
    email_svc: EmailService = Depends(get_email_service),
):
    await email_svc.send_email(
        to_address="support@example.com",
        subject="Contact form",
        html_body="<p>Hello</p>",
        text_body="Hello",
    )
```

### Blob Storage Service

```python
from vibetuner.services import get_blob_service
from vibetuner.services.blob import BlobService

@router.post("/upload")
async def upload(
    blobs: BlobService = Depends(get_blob_service),
):
    await blobs.put_object(...)
```

### Runtime Config

```python
from vibetuner.services import get_runtime_config
from vibetuner.runtime_config import RuntimeConfig

@router.get("/settings")
async def app_settings(
    config: RuntimeConfig = Depends(get_runtime_config),
):
    dark_mode = await config.get("features.dark_mode")
    return {"dark_mode": dark_mode}
```

The dependency automatically refreshes the config cache if it is stale.

## Health Check Endpoints

Built-in health endpoints are available at `/health` for liveness probes,
readiness checks, and service diagnostics.

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Fast liveness check (status + version + uptime) |
| `GET /health?detailed=true` | Checks all configured services with latency |
| `GET /health/ready` | Readiness probe — all services must be reachable |
| `GET /health/ping` | Ultra-fast liveness — returns `{"status": "ok"}` |
| `GET /health/id` | Instance identification (slug, port, PID, startup time) |

### Liveness Check

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0", "uptime_seconds": 3600}
```

### Detailed Health Check

```bash
curl http://localhost:8000/health?detailed=true
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "uptime_seconds": 3600,
#   "services": {
#     "mongodb": {"status": "connected", "latency_ms": 2.1},
#     "redis": {"status": "connected", "latency_ms": 0.5}
#   }
# }
```

If any service reports an error, the overall status becomes `"degraded"`.

### Readiness Probe

Use `/health/ready` in Kubernetes or Docker health checks to ensure all
services are reachable before routing traffic:

```yaml
# docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
  interval: 30s
  timeout: 5s
  retries: 3
```

Services checked automatically based on configuration: MongoDB, Redis,
S3/R2 endpoint, and email (Resend or Mailjet).

## Debugging

### View Logs

```bash
# Docker mode
docker compose logs -f web
# Local mode
# Logs print to stdout
```

### Access Database

```bash
# MongoDB
docker compose exec mongodb mongosh

# PostgreSQL
docker compose exec postgres psql -U postgres
```

### Interactive Shell

```bash
# Python shell with app context
just shell
```

## Testing

### Run Tests

```bash
pytest
```

### Test Coverage

```bash
pytest --cov=src/app
```

### Integration Tests

Integration tests should use a real database (not mocks):

```python
import pytest
from app.models import Post

@pytest.mark.asyncio
async def test_create_post():
    post = Post(title="Test", content="Content")
    await post.insert()  # MongoDB with Beanie
    found = await Post.get(post.id)
    assert found.title == "Test"
```

### Built-in Test Fixtures

Vibetuner provides pytest fixtures in `vibetuner.testing` for common
test scenarios. Add this import to your `conftest.py`:

```python
# tests/conftest.py
from vibetuner.testing import *  # noqa: F403
```

#### `vibetuner_client` — Async HTTP Test Client

Full-stack async test client with middleware, sessions, and HTMX support:

```python
async def test_homepage(vibetuner_client):
    resp = await vibetuner_client.get("/")
    assert resp.status_code == 200
```

Override `vibetuner_app` fixture to supply a custom FastAPI app instance.

#### `vibetuner_db` — Shared MongoDB Test Database

Creates a single MongoDB database for the whole test session, runs Beanie
index registration once, and **truncates every non-system collection
before and after each test** so each test starts with empty collections:

```python
async def test_create_post(vibetuner_db):
    post = Post(title="Test", content="Content")
    await post.insert()
    assert await Post.get(post.id) is not None
```

Skips the test automatically if `MONGODB_URL` is not set.

**Caveats:**

- All tests in a session share the same database. Don't assert on
  database-level state (existence, name, full collection drops) or on
  indexes being absent.
- Indexes (including unique constraints) are built once at session
  scope and persist across tests. `DuplicateKeyError` is still raised
  by unique violations.
- Concurrent runs need `pytest-xdist`; the session DB name includes
  the worker id (`PYTEST_XDIST_WORKER`) so workers don't collide.
- If a test crashes mid-run, the next test re-truncates on setup so
  state is self-healing.

#### `mock_auth` — Authentication Mocking

Patches the auth backend so requests appear authenticated without real
sessions or cookies:

```python
async def test_profile(vibetuner_client, mock_auth):
    mock_auth.login(name="Alice", email="alice@example.com")
    resp = await vibetuner_client.get("/user/profile")
    assert resp.status_code == 200

    mock_auth.logout()
    resp = await vibetuner_client.get("/user/profile")
    assert resp.status_code != 200
```

#### `mock_tasks` — Background Task Mocking

Test background task enqueuing without Redis:

```python
from unittest.mock import patch

async def test_signup(vibetuner_client, mock_tasks):
    with patch(
        "app.tasks.emails.send_welcome_email",
        mock_tasks.send_welcome_email,
    ):
        resp = await vibetuner_client.post("/signup", data={...})
    assert mock_tasks.send_welcome_email.enqueue.called
```

#### `override_config` — Runtime Config Overrides

Override `RuntimeConfig` values for a single test with automatic cleanup:

```python
async def test_feature_flag(override_config):
    await override_config("features.dark_mode", True)
    # Test code that reads the config value
```

## Code Quality

### Format Code

```bash
just format
```

Runs:

- `ruff format` for Python

### Check Code

```bash
just lint
```

Runs:

- `ruff check` for Python
- Type checking
- Template validation

## Environment Configuration

### Development Settings

Copy `.env.local` to `.env`:

```bash
cp .env.local .env
```

Edit as needed:

```bash
# .env
# MongoDB
MONGODB_URL=mongodb://localhost:27017/myapp
# Or SQL database (PostgreSQL, MySQL, MariaDB, SQLite)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/myapp
# DATABASE_URL=sqlite+aiosqlite:///./data.db

SESSION_KEY=your-secret-key-here
DEBUG=true
# OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Production Settings

Use environment variables or `.env` file in production:

```bash
# MongoDB
MONGODB_URL=mongodb://prod-server:27017/myapp
# Or SQL database
DATABASE_URL=postgresql+asyncpg://user:pass@prod-server/myapp

SESSION_KEY=very-secret-key
DEBUG=false
```

## Keeping the Scaffold Up to Date

When new versions of the template ship, update your project using either:

- `vibetuner scaffold update` – works from anywhere; replays Copier with your
saved answers.
- `just update-scaffolding` – runs inside the generated project and wraps
`copier update` plus dependency sync.

Both commands modify tracked files, so commit or stash your work beforehand and
review the changes afterward. See the
[Scaffolding Reference](scaffolding.md#updating-existing-projects) for a deeper
walkthrough.

## Dependency Management

### Add Python Package

```bash
uv add package-name
```

### Add JavaScript Package

```bash
bun add package-name
```

### Sync All Dependencies

```bash
just sync
```

Syncs both Python and JavaScript dependencies.

## Common Import Pitfalls

When working with `tune.py` and the framework internals, certain import patterns cause
circular imports. This section explains the rules and how to avoid problems.

### Why Circular Imports Happen

The framework loads your `tune.py` via `vibetuner.loader` at startup. If `tune.py` imports
a module that itself imports `vibetuner.loader` (or anything that triggers `tune.py` to be
loaded again), you get a circular import.

### Safe vs. Unsafe Imports in tune.py

| Import | Safe? | Notes |
|--------|-------|-------|
| `from vibetuner.rendering import render_template` | Yes | `rendering.py` lives outside `vibetuner.frontend` specifically to avoid cycles |
| `from vibetuner import render_template` | Yes | Re-export of the above |
| `from vibetuner.frontend.templates import render_template` | No | `vibetuner.frontend.__init__` imports from `loader`, which imports `tune.py` |
| `from vibetuner.frontend import localized` | No | Same reason — triggers `vibetuner.frontend.__init__` |
| `from vibetuner.frontend.routing import LocalizedRouter` | Yes | Direct submodule import bypasses `__init__` |

**Rule of thumb:** never import from `vibetuner.frontend` (the package) in `tune.py`.
Import from specific submodules (`vibetuner.frontend.routing`, `vibetuner.frontend.deps`)
or use the top-level re-exports (`vibetuner.rendering`).

### Background Task Modules

Task modules listed in `VibetunerApp.tasks` are imported after model initialization.
If a task module imports a model at the top level, the model class must already be defined
in `src/app/models/`:

```python
# src/app/tasks/emails.py
from vibetuner.tasks.worker import get_worker
from app.models.user import User  # OK — models are initialized before tasks load

worker = get_worker()

@worker.task()
async def send_welcome(user_id: str):
    user = await User.get(user_id)
    ...
```

### Lifespan and Lazy Imports

The framework's `lifespan()` function uses lazy imports to break potential cycles:

```python
# vibetuner/frontend/lifespan.py
async def lifespan(app):
    # Lazy import — tune.py may import vibetuner.frontend submodules
    from vibetuner.loader import load_app_config
    app_config = load_app_config()
    ...
```

If you provide a custom `frontend_lifespan` in `tune.py`, follow the same pattern — use
lazy imports for any `vibetuner.frontend` submodules you need inside the lifespan body:

```python
# src/app/tune.py
from contextlib import asynccontextmanager
from vibetuner import VibetunerApp
from vibetuner.frontend.lifespan import base_lifespan

@asynccontextmanager
async def my_lifespan(app):
    async with base_lifespan(app):
        # Lazy import to avoid circular dependency
        from vibetuner.frontend.hotreload import hotreload  # noqa: F811
        ...
        yield

app = VibetunerApp(frontend_lifespan=my_lifespan)
```

### Quick Checklist

1. In `tune.py`, import from `vibetuner.*` (top-level) or specific submodules, never from
   `vibetuner.frontend` as a package.
2. Task modules can import models at the top level — they load after model init.
3. Custom lifespans should lazy-import `vibetuner.frontend.*` inside the function body.

## Next Steps

- [Authentication](authentication.md) - Set up OAuth providers
- [Deployment](deployment.md) - Deploy to production
- [Architecture](architecture.md) - Understand the system design
