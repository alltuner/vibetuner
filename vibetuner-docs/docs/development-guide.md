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
- Frontend asset compilation with watch mode

Changes to Python code, templates, and assets automatically reload.

### Local Development

Run services locally without Docker:

```bash
just install-deps            # Run once after cloning or updating lockfiles
just local-all               # Runs server + assets with auto-port (recommended)
just local-all-with-worker   # Includes background worker (requires Redis)
```

A database (MongoDB or SQL) is required if using database features. Redis is only required if
background jobs are enabled.

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

For SQL databases, create tables with: `vibetuner db create-schema`

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
from vibetuner.services.email import send_email

worker = get_worker()

@worker.task()
async def send_welcome_email(user_id: str):
    user = await UserModel.get(user_id)
    if user:
        await send_email(
            to_email=user.email,
            subject="Welcome!",
            html_content="<h1>Welcome!</h1>"
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

#### Using `locale_names` for Language Selectors

The `locale_names` dict maps language codes to their native display names, sorted alphabetically:

```html
<select name="language">
    {% for code, name in locale_names.items() %}
        <option value="{{ code }}"
                {% if code == current_language %}selected{% endif %}>
            {{ name }}
        </option>
    {% endfor %}
</select>
```

Example output: `{"ca": "Català", "en": "English", "es": "Español"}`

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

1. Query parameter (`?l=es`)
2. URL path prefix (`/ca/...`)
3. User preference (from session, for authenticated users)
4. Cookie (`language` cookie)
5. Accept-Language header (browser preference)
6. Default language

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

Include the router in your app (via `tune.py` routes or `app.include_router()`):

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.routes.posts import post_routes

app = VibetunerApp(routes=[post_routes])
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
- `GET /posts?q=python` — text search across searchable fields
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

Connect an SSE endpoint to HTMX with the `sse-connect` extension:

```html
<div hx-ext="sse" sse-connect="/events/notifications">
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
S3/R2 endpoint, and email (Mailjet).

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

#### `vibetuner_db` — Temporary MongoDB Database

Creates a unique test database, initialises Beanie with all registered
models, and drops the database on teardown:

```python
async def test_create_post(vibetuner_db):
    post = Post(title="Test", content="Content")
    await post.insert()
    assert await Post.get(post.id) is not None
```

Skips the test automatically if `MONGODB_URL` is not set.

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

SECRET_KEY=your-secret-key-here
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

SECRET_KEY=very-secret-key
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
