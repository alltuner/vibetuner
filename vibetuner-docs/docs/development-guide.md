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

- MongoDB database
- Redis (if background jobs enabled)
- FastAPI application with auto-reload
- Frontend asset compilation with watch mode

Changes to Python code, templates, and assets automatically reload.

### Local Development

Run services locally without Docker:

```bash
# Terminal 1: Frontend assets
bun dev
# Terminal 2: Backend server
just local-dev
```

Requires MongoDB and Redis running locally.

## Justfile Commands Reference

All project management tasks use `just` (command runner). Run `just` without arguments to see all
available commands.

### Development

```bash
just dev                     # Docker development with hot reload (recommended)
just local-dev PORT=8000     # Local development without Docker
just worker-dev              # Background worker (if background jobs enabled)
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

Create models in `src/app/models/`:

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

Register in `src/app/models/__init__.py`:

```python
from app.models.post import Post
__all__ = ["Post"]
```

The model will be automatically registered with MongoDB on startup.

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
# Connect to MongoDB
docker compose exec mongodb mongosh
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

Integration tests should use real MongoDB (not mocks):

```python
import pytest
from app.models import Post
@pytest.mark.asyncio
async def test_create_post():
post = Post(title="Test", content="Content")
await post.insert()
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
DATABASE_URL=mongodb://localhost:27017/myapp
SECRET_KEY=your-secret-key-here
DEBUG=true
# OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Production Settings

Use environment variables or `.env` file in production:

```bash
DATABASE_URL=mongodb://prod-server:27017/myapp
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
