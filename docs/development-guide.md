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
# src/app/tasks/email.py
from vibetuner.services.email import send_email

async def send_welcome_email(user_id: str):
    # Fetch user from database
    # Send welcome email
    pass
```

Queue jobs from your routes:

```python
from streaq import queue
from app.tasks.email import send_welcome_email

@router.post("/signup")
async def signup(email: str):
    # Create user
    await queue(send_welcome_email, user.id)
    return {"message": "Welcome email queued"}
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
<button
  hx-get="/blog?page=2"
  hx-target="#posts"
  hx-swap="beforeend"
  class="btn btn-primary">
  Load More
</button>

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
- `djlint` for templates

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
