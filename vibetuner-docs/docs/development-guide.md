# Development Guide

Daily development workflow for Vibetuner projects.

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

### Parallel Development

```bash
just feature-new NAME        # Create new feature worktree
just feature-list            # List all feature worktrees
just feature-done [NAME]     # Remove worktree + delete merged branch
just feature-drop [NAME]     # Force remove worktree + delete branch
just feature-rebase          # Sync current branch with origin/main
```

## Parallel Development with Worktrees

Work on multiple features simultaneously using git worktrees. Each worktree is an isolated
copy of the repository with its own branch, allowing true parallel development.

### When to Use Worktrees

| Approach | Use When |
|----------|----------|
| Worktrees (`feature-new`) | Working on multiple features, need clean isolation, instant context switching |
| Simple branch (`git checkout`) | Single feature at a time, quick fixes, prefer simpler workflow |

### Creating a Feature Worktree

```bash
just feature-new feat/user-dashboard
# Creates worktrees/a1b2c3d4/ with branch feat/user-dashboard
# Symlinks .env for shared configuration
# Runs mise trust if available

cd worktrees/a1b2c3d4
# Work on your feature...
```

### Listing Feature Worktrees

```bash
just feature-list
# Shows all active feature worktrees with their branches and paths
```

### Completing a Feature

After your PR is merged, clean up the worktree and branch:

```bash
# Auto-detect from current directory (run from within the worktree)
just feature-done

# By branch name
just feature-done feat/user-dashboard

# By directory path
just feature-done ./worktrees/a1b2c3d4
```

If you're inside the worktree when running `feature-done`, you'll be reminded to `cd` back to
the main repository since the directory will be deleted.

### Abandoning Unmerged Work

Use `feature-drop` to force-remove a worktree even if the branch has unmerged changes:

```bash
just feature-drop feat/abandoned-idea
```

### Keeping Features Up to Date

Rebase your feature branch on latest main:

```bash
cd worktrees/a1b2c3d4
just feature-rebase
# Fetches origin/main and rebases your branch on top
```

## Common Tasks

### Adding New Routes

Create a new file in `src/app/frontend/routes/`:

```python
# src/app/frontend/routes/blog.py
from fastapi import APIRouter
router = APIRouter(prefix="/blog", tags=["blog"])
@router.get("/")
async def list_posts():
return {"posts": []}
```

Register in `src/app/frontend/__init__.py`:

```python
from app.frontend.routes import blog
app.include_router(blog.router)
```

### Adding Database Models

Create models in `src/app/models/`. The approach depends on your database choice:

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

Register models in `src/app/models/__init__.py`:

```python
from app.models.post import Post
__all__ = ["Post"]
```

### Creating Templates

Add templates in `templates/`:

```html
<!-- templates/blog/list.html.jinja -->
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
{% endblock %}
```

### Adding Custom Template Filters

Create custom Jinja2 filters in `src/app/frontend/templates.py`:

```python
# src/app/frontend/templates.py
from vibetuner.frontend.templates import register_filter

@register_filter()
def uppercase(value):
    """Convert value to uppercase"""
    return str(value).upper()

@register_filter("money")
def format_money(value):
    """Format value as USD currency"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)
```

Use in templates:

```html
<h1>{{ user.name | uppercase }}</h1>
<p>Price: {{ product.price | money }}</p>
```

The `@register_filter()` decorator automatically registers filters with the Jinja
environment. If no name is provided, the function name becomes the filter name.

### Adding Background Jobs

If you enabled background jobs, create tasks in `src/app/tasks/`:

```python
# src/app/tasks/emails.py
from vibetuner.tasks.worker import worker
from vibetuner.models import UserModel
from vibetuner.services.email import send_email

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

Register tasks in `src/app/tasks/__init__.py`:

```python
# src/app/tasks/__init__.py
__all__ = ["emails"]
from . import emails  # noqa: F401
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
| `/dashboard` (anonymous) | Redirects to `/{default_lang}/dashboard` (if route uses `LangPrefixDep`) |
| `/dashboard` (logged-in) | Serves directly, uses profile language |
| `/xx/dashboard` (invalid) | Returns 404 Not Found |
| `/ca` | Redirects to `/ca/` |
| `/static/...` | Bypassed, serves static file directly |

#### Requiring Language Prefix for SEO Routes

Use `LangPrefixDep` to mark routes that should redirect anonymous users to prefixed URLs:

```python
from fastapi import Request
from vibetuner.frontend import LangPrefixDep
from vibetuner.frontend.templates import render_template

@router.get("/privacy")
async def privacy(request: Request, _: LangPrefixDep):
    return render_template("privacy.html.jinja", request)
```

With this dependency:

- Anonymous users visiting `/privacy` are redirected to `/en/privacy` (or their detected language)
- Authenticated users can access either `/privacy` or `/en/privacy`
- Search engines see clean, language-specific URLs

#### Generating Language-Prefixed URLs in Templates

Use `lang_url_for` to generate URLs with the current language prefix:

```html
<a href="{{ lang_url_for(request, 'privacy') }}">Privacy Policy</a>
<!-- Output: /ca/privacy (if current language is Catalan) -->
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
<link rel="alternate" hreflang="x-default" href="https://example.com/en/privacy" />
```

#### Complete Example

Route definition:

```python
# src/app/frontend/routes/legal.py
from fastapi import APIRouter, Request
from vibetuner.frontend import LangPrefixDep
from vibetuner.frontend.templates import render_template

router = APIRouter(tags=["legal"])

@router.get("/privacy")
async def privacy(request: Request, _: LangPrefixDep):
    return render_template("legal/privacy.html.jinja", request)

@router.get("/terms")
async def terms(request: Request, _: LangPrefixDep):
    return render_template("legal/terms.html.jinja", request)
```

Template with hreflang:

```html
<!-- templates/legal/privacy.html.jinja -->
{% extends "base/skeleton.html.jinja" %}

{% block head_extra %}
{{ hreflang_tags(request, supported_languages, default_language)|safe }}
{% endblock %}

{% block content %}
<h1>{% trans %}Privacy Policy{% endtrans %}</h1>
<!-- Content -->
{% endblock %}
```

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

## Next Steps

- [Authentication](authentication.md) - Set up OAuth providers
- [Deployment](deployment.md) - Deploy to production
- [Architecture](architecture.md) - Understand the system design
