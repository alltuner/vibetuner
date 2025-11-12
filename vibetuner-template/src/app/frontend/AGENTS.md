# Application Frontend Routes

**YOUR WEB ROUTES GO HERE** - Define your application's HTTP endpoints and handlers.

## What Goes Here

Create your application-specific routes in the `routes/` subdirectory:

- Public pages (landing, about, pricing)
- Dashboard and authenticated pages
- API endpoints
- Form handlers
- HTMX partial responses
- Any custom HTTP handlers

## Directory Structure

```text
src/app/frontend/
├── routes/              # ✅ ADD YOUR ROUTES HERE
│   ├── __init__.py     # Register routes (edit app_router)
│   ├── dashboard.py    # Example route module
│   └── api.py          # Example API routes
├── lifespan.py         # Application startup/shutdown lifecycle (optional)
└── oauth.py            # OAuth provider configuration
```

## Route Pattern

```python
# routes/dashboard.py
from fastapi import APIRouter, Request, Depends, HTTPException
from vibetuner.frontend.deps import get_current_user
from vibetuner.frontend.templates import render_template
from vibetuner.models import UserModel
from app.models.post import Post

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
async def dashboard_home(
    request: Request,
    user: UserModel = Depends(get_current_user)
):
    """Dashboard home page."""
    posts = await Post.find(Post.author.id == user.id).to_list()

    return render_template(
        "dashboard/home.html.jinja",
        request,
        {
            "user": user,
            "posts": posts,
            "stats": {"total_posts": len(posts)}
        }
    )

@router.post("/posts")
async def create_post(
    request: Request,
    title: str,
    content: str,
    user: UserModel = Depends(get_current_user)
):
    """Create a new post."""
    post = Post(title=title, content=content, author=user)
    await post.insert()

    # Return HTMX partial
    return render_template(
        "dashboard/partials/post_item.html.jinja",
        request,
        {"post": post}
    )
```

## Registering Routes

Edit `routes/__init__.py` to register your route modules:

```python
# routes/__init__.py
from fastapi import APIRouter

from .dashboard import router as dashboard_router
from .api import router as api_router
from .public import router as public_router

# Application router
app_router = APIRouter()

# Register all route modules
app_router.include_router(public_router)
app_router.include_router(dashboard_router)
app_router.include_router(api_router, prefix="/api")
```

## Available from Core

### Dependencies

```python
from vibetuner.frontend.deps import (
    get_current_user,           # Require auth (raises 403)
    get_current_user_optional,  # Optional auth (returns None)
    LangDep,                    # Current language
    MagicCookieDep,             # Magic link cookie
)

@router.get("/profile")
async def profile(user: UserModel = Depends(get_current_user)):
    # user is guaranteed to be authenticated
    pass

@router.get("/")
async def home(user: UserModel | None = Depends(get_current_user_optional)):
    # user may be None if not authenticated
    pass
```

### Template Rendering

```python
from vibetuner.frontend.templates import render_template

return render_template(
    "template_path.html.jinja",
    request,
    {
        "custom_var": value,
        # Automatic context already includes:
        # - request
        # - DEBUG
        # - hotreload (dev mode)
        # - project settings
        # - language info
    }
)
```

### OAuth Configuration

Edit `oauth.py` to configure OAuth providers:

```python
# src/app/frontend/oauth.py
from vibetuner.frontend.oauth import OAuthProvider

def get_oauth_providers() -> dict[str, OAuthProvider]:
    """Define OAuth providers for your app."""
    return {
        "google": OAuthProvider(
            name="Google",
            client_id="your-client-id",
            client_secret="your-secret",
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
            scopes=["openid", "email", "profile"],
        ),
        # Add more providers...
    }
```

### Extending Application Lifespan

The scaffolding provides a `base_lifespan` that handles core startup/shutdown tasks (MongoDB
initialization, hot-reload, etc.). You can extend this by creating `lifespan.py` to add your own
startup and shutdown logic:

```python
# src/app/frontend/lifespan.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from vibetuner.config import settings
from vibetuner.frontend.lifespan import base_lifespan
from vibetuner.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.project.project_name} frontend...")

    # Add any startup tasks here (e.g., initialize cache, start background services)

    async with base_lifespan(app):
        yield
        logger.info(f"Stopping {settings.project.project_name} frontend...")

    # Add any teardown tasks here (e.g., close connections, cleanup resources)

    logger.info(f"{settings.project.project_name} has shut down.")
```

**Key points:**

- Your `lifespan` function wraps `base_lifespan` using `async with`
- Add startup code before the `async with` block
- Add teardown code after the `yield` inside the context manager
- The base lifespan handles MongoDB, hot-reload, and other core tasks automatically
- If you don't need custom lifecycle management, you can omit this file entirely

## Core Default Routes

These routes are automatically available (DO NOT DUPLICATE):

- `GET /` - Index/landing page
- `GET /login` - Login page
- `POST /auth/magic-link` - Send magic link
- `GET /auth/{provider}` - OAuth login
- `GET /auth/{provider}/callback` - OAuth callback
- `GET /health/ping` - Health check
- `GET /user/profile` - User profile
- `GET /lang/set/{code}` - Set language
- `GET /debug/` - Debug info (DEBUG mode only)

## Common Patterns

### Full Page Routes

```python
@router.get("/about")
async def about(request: Request):
    """About page."""
    return render_template("about.html.jinja", request, {})
```

### Protected Routes

```python
@router.get("/settings")
async def settings(
    request: Request,
    user: UserModel = Depends(get_current_user)
):
    """User settings page (requires auth)."""
    return render_template("settings.html.jinja", request, {"user": user})
```

### API Endpoints

```python
@router.get("/api/posts/{post_id}")
async def get_post(post_id: str):
    """Get post by ID."""
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": str(post.id), "title": post.title}

@router.post("/api/posts")
async def create_post_api(
    title: str,
    content: str,
    user: UserModel = Depends(get_current_user)
):
    """Create post via API."""
    post = Post(title=title, content=content, author=user)
    await post.insert()
    return {"id": str(post.id), "title": post.title}
```

### HTMX Partials

```python
@router.get("/posts/{post_id}/comments")
async def load_comments(request: Request, post_id: str):
    """Load comments partial for HTMX."""
    comments = await Comment.find(Comment.post_id == post_id).to_list()

    # Return just the HTML fragment
    return render_template(
        "partials/comments.html.jinja",
        request,
        {"comments": comments}
    )

@router.post("/posts/{post_id}/like")
async def like_post(
    request: Request,
    post_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Like post (HTMX action)."""
    post = await Post.get(post_id)
    post.likes += 1
    await post.save()

    # Return updated button HTML
    return render_template(
        "partials/like_button.html.jinja",
        request,
        {"post": post, "liked": True}
    )
```

### Form Handling

```python
from fastapi import Form
from pydantic import BaseModel, ValidationError

class PostForm(BaseModel):
    title: str
    content: str
    tags: list[str] = []

@router.post("/posts/create")
async def create_post_form(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    user: UserModel = Depends(get_current_user)
):
    """Handle post creation form."""
    try:
        # Validate
        form_data = PostForm(
            title=title,
            content=content,
            tags=tags.split(",") if tags else []
        )

        # Create post
        post = Post(**form_data.model_dump(), author=user)
        await post.insert()

        # Redirect or return success
        return RedirectResponse(f"/posts/{post.id}", status_code=303)

    except ValidationError as e:
        # Return errors
        return render_template(
            "posts/form.html.jinja",
            request,
            {"errors": e.errors(), "form": {"title": title, "content": content}}
        )
```

### File Upload

```python
from fastapi import File, UploadFile
from vibetuner.services.blob import blob_service

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user: UserModel = Depends(get_current_user)
):
    """Handle file upload."""
    # Read file
    file_bytes = await file.read()

    # Upload to blob storage
    blob = await blob_service.upload(file_bytes, file.filename)

    # Return upload result
    return {
        "id": str(blob.id),
        "filename": file.filename,
        "size": len(file_bytes)
    }
```

### Streaming Responses

```python
from fastapi.responses import StreamingResponse
import asyncio

@router.get("/stream")
async def stream_data(user: UserModel = Depends(get_current_user)):
    """Server-sent events stream."""
    async def event_generator():
        for i in range(10):
            await asyncio.sleep(1)
            yield f"data: {i}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

## Response Types

### HTML (Default)

```python
return render_template("page.html.jinja", request, context)
```

### JSON

```python
return {"key": "value"}  # Automatic JSON serialization
```

### Redirect

```python
from fastapi.responses import RedirectResponse

return RedirectResponse("/success", status_code=303)
```

### File Download

```python
from fastapi.responses import FileResponse

return FileResponse(
    "path/to/file.pdf",
    filename="download.pdf",
    media_type="application/pdf"
)
```

## Error Handling

```python
from fastapi import HTTPException

@router.get("/posts/{post_id}")
async def get_post(post_id: str):
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    return render_template("post.html.jinja", request, {"post": post})

# Custom error handler
from fastapi.responses import HTMLResponse

@router.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return render_template("errors/404.html.jinja", request, {})
```

## Testing Routes

```python
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

@pytest.fixture
async def client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

async def test_dashboard(client, authenticated_user):
    response = await client.get("/dashboard")
    assert response.status_code == 200
    assert "Dashboard" in response.text

async def test_create_post_api(client, authenticated_user):
    response = await client.post(
        "/api/posts",
        json={"title": "Test", "content": "Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test"
```

## Best Practices

1. **Use route prefixes** - Organize related routes with `APIRouter(prefix="/section")`
2. **Tag your routes** - Add `tags=["category"]` for automatic API docs grouping
3. **Type everything** - Use type hints for all parameters
4. **Validate inputs** - Use Pydantic models for complex data
5. **Handle errors** - Use HTTPException for expected errors
6. **Depend on core** - Import deps and utilities from core, don't recreate them
7. **Keep routes thin** - Move business logic to services
8. **Return appropriate responses** - HTML for pages, JSON for APIs, partials for HTMX

## HTMX Integration

See the `jinja-htmx-frontend` agent for detailed HTMX patterns and template development.

## Need Help?

- Core frontend changes: `https://github.com/alltuner/vibetuner`
- FastAPI docs: `https://fastapi.tiangolo.com/`
- HTMX docs: `https://htmx.org/docs/`
