# Application Root

**YOUR APPLICATION CODE LIVES HERE** - This is where you build your project.

## Structure

```
src/app/
├── __init__.py           # Application package root
├── config.py             # Application-specific configuration
├── cli/                  # CLI commands
├── frontend/             # Web routes and handlers
│   ├── routes/          # ✅ ADD YOUR ROUTES HERE
│   └── oauth.py         # OAuth configuration
├── models/              # ✅ ADD YOUR MODELS HERE
├── services/            # ✅ ADD YOUR SERVICES HERE
└── tasks/               # ✅ ADD YOUR TASKS HERE (if enabled)
    └── worker.py        # Task worker setup
```

## Key Concepts

### Core vs App

- **`src/core/`** - Immutable scaffolding code (DO NOT MODIFY)
  - User authentication, OAuth, email verification
  - Email service, blob storage
  - Base templates, middleware, default routes
  - MongoDB setup, logging, configuration

- **`src/app/`** - Your application code (THIS IS YOUR SPACE)
  - Your business logic
  - Your data models
  - Your API routes
  - Your background tasks
  - Your CLI commands

### Configuration

**`src/app/config.py`** - Application-specific settings:
```python
from core.config import project_settings
from core.versioning import version

class Configuration(BaseSettings):
    # Your app settings
    debug: bool = False
    version: str = version
    
    # AWS, R2, or other service credentials
    aws_access_key_id: SecretStr | None = None
    
    # Add your configuration variables here
```

**`src/core/config.py`** - Project-level settings (read-only):
- Project name, slug, description
- MongoDB URL, Redis URL
- Supported languages
- Company info, copyright

### Importing from Core

```python
# Models
from core.models import UserModel, OAuthAccountModel
from core.models.mixins import TimeStampMixin

# Services
from core.services.email import send_email
from core.services.blob import blob_service

# Frontend utilities
from core.frontend.deps import get_current_user
from core.frontend.templates import render_template

# Configuration
from core.config import project_settings
from app.config import settings
```

## Quick Start Patterns

### Adding a New Feature

1. **Model** - Define data structure in `models/`
2. **Service** - Business logic in `services/`
3. **Route** - API endpoints in `frontend/routes/`
4. **Template** - UI in `templates/app/frontend/`
5. **Task** - Background jobs in `tasks/` (if enabled)

### Example: Blog Posts

```python
# models/post.py
from beanie import Document
from core.models.mixins import TimeStampMixin
from core.models import UserModel

class Post(Document, TimeStampMixin):
    title: str
    content: str
    author: Link[UserModel]
    
    class Settings:
        name = "posts"
        indexes = ["author"]

# frontend/routes/posts.py
from fastapi import APIRouter, Request, Depends
from core.frontend.deps import get_current_user
from core.frontend.templates import render_template
from app.models.post import Post

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/")
async def list_posts(request: Request):
    posts = await Post.find_all().to_list()
    return render_template("posts/list.html.jinja", request, {"posts": posts})

@router.post("/")
async def create_post(
    request: Request,
    title: str,
    content: str,
    user=Depends(get_current_user)
):
    post = Post(title=title, content=content, author=user)
    await post.insert()
    return {"id": str(post.id)}
```

## Module Guides

- **`cli/`** - See `cli/AGENTS.md` for CLI command patterns
- **`frontend/`** - See `frontend/AGENTS.md` for route patterns
- **`models/`** - See `models/AGENTS.md` for model patterns
- **`services/`** - See `services/AGENTS.md` for service patterns
- **`tasks/`** - See `tasks/AGENTS.md` for background task patterns

## Important Notes

- **Never modify `src/core/`** - File issues at `https://github.com/alltuner/scaffolding`
- **Always use type hints** - FastAPI and Beanie rely on them
- **Run `ruff format .`** after changes - Keep code consistent
- **Use async/await** - The stack is fully async
