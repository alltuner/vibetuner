# Architecture

Understanding Vibetuner's system design and structure.

## High-Level Overview

Vibetuner generates full-stack web applications with clear separation between framework code and application code.

```
┌─────────────────────────────────────────────┐
│           Your Application                   │
│  (src/app/ - Routes, Models, Services)      │
├─────────────────────────────────────────────┤
│          Vibetuner Framework                 │
│   (src/vibetuner/ - Auth, DB, Core)        │
├─────────────────────────────────────────────┤
│     FastAPI + MongoDB + HTMX + Redis        │
└─────────────────────────────────────────────┘
```

## Three-Package Architecture

Vibetuner consists of three components:

### 1. Scaffolding Template

**Location**: Root repository (`copier.yml`, `copier-template/`)

The Copier-based template that generates new projects:

- Interactive project setup
- Configurable features (OAuth, background jobs, etc.)
- Generates complete project structure
- Updates existing projects

**Command**: `uvx vibetuner scaffold new my-app`

**Note**: A `template/` symlink exists for backwards compatibility.

### 2. Python Package (`vibetuner`)

**Location**: `vibetuner-py/`

Published to PyPI, provides:

- Core framework code
- Authentication system
- Database integration
- Email and storage services
- CLI commands
- Blessed dependency stack

**Install**: `uv add vibetuner`

### 3. JavaScript Package (`@alltuner/vibetuner`)

**Location**: `vibetuner-js/`

Published to npm, provides:

- Frontend build dependencies (Tailwind, esbuild, etc.)
- Version-locked with Python package
- No runtime dependencies

**Install**: `bun add @alltuner/vibetuner`

## Generated Project Structure

```
my-app/
├── src/
│   ├── vibetuner/              # Framework code (immutable)
│   │   ├── frontend/           # FastAPI app, middleware, auth
│   │   ├── models/             # User, OAuth models
│   │   ├── services/           # Email, storage, external APIs
│   │   ├── cli/                # Command-line interface
│   │   ├── config.py           # Settings management
│   │   └── mongo.py            # Database connection
│   │
│   └── app/                    # Your code (edit freely)
│       ├── frontend/
│       │   ├── __init__.py     # FastAPI app initialization
│       │   └── routes/         # Your HTTP endpoints
│       ├── models/             # Your database models
│       ├── services/           # Your business logic
│       └── tasks/              # Background jobs (optional)
│
├── templates/                  # Jinja2 templates
│   ├── base/                   # Base layouts
│   ├── frontend/               # Page templates
│   └── emails/                 # Email templates
│
├── assets/                     # Static assets
│   ├── config.css              # Tailwind CSS config
│   ├── config.js               # JavaScript entry
│   └── statics/                # Compiled output
│
├── translations/               # i18n files
│   └── {locale}/LC_MESSAGES/
│
├── Dockerfile                  # Multi-stage production build
├── compose.dev.yml             # Docker Compose for dev
├── compose.prod.yml            # Docker Compose for prod
├── pyproject.toml              # Python dependencies
├── package.json                # JavaScript dependencies
├── justfile                    # Command runner
└── .env                        # Environment variables
```

## Request Flow

### 1. HTTP Request

```
Client → Nginx/Caddy → FastAPI (Granian) → Route Handler
```

### 2. Route Handler

```python
# src/app/frontend/routes/blog.py
@router.get("/blog/{post_id}")
async def view_post(post_id: str):
    post = await Post.get(post_id)
    return templates.TemplateResponse("blog/post.html.jinja", {
        "post": post
    })
```

### 3. Database Query

```
Route → Beanie ODM → Motor (async) → MongoDB
```

### 4. Template Rendering

```
Jinja2 Template → HTML with HTMX → Client
```

### 5. HTMX Interaction

```
User Action → HTMX Request → FastAPI → Partial HTML → Update DOM
```

## Core Components

### FastAPI Application

**Location**: `src/app/frontend/__init__.py`

Application initialization and middleware stack:

```python
from fastapi import FastAPI
from vibetuner.frontend.middleware import setup_middleware
from app.frontend.routes import blog, api

app = FastAPI()
setup_middleware(app)  # Auth, sessions, i18n, static files

app.include_router(blog.router)
app.include_router(api.router)
```

### Database Layer

**Location**: `src/vibetuner/mongo.py`

MongoDB connection and model registration:

```python
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from vibetuner.models import User
from app.models import Post, Comment

async def init_db():
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[User, Post, Comment]
    )
```

### Authentication System

**Location**: `src/vibetuner/frontend/auth.py`

Dual authentication with OAuth and magic links:

```
OAuth Flow:
1. User clicks "Sign in with Google"
2. Redirect to Google OAuth
3. Google redirects back with code
4. Exchange code for user info
5. Create/update user in database
6. Create session

Magic Link Flow:
1. User enters email
2. Generate secure token
3. Send email with link
4. User clicks link
5. Verify token
6. Create session
```

### Session Management

HTTP-only, secure cookies with server-side validation:

```python
session_data = {
    "user_id": str(user.id),
    "created_at": datetime.utcnow()
}
session_id = secrets.token_urlsafe(32)
await redis.setex(f"session:{session_id}", SESSION_MAX_AGE, json.dumps(session_data))
```

### Background Jobs

**Location**: `src/app/tasks/`

Optional Redis-based background processing:

```python
# Define task
async def send_email(user_id: str, template: str):
    user = await User.get(user_id)
    await email_service.send(user.email, template)

# Queue task
from streaq import queue
await queue(send_email, user_id="123", template="welcome")
```

Worker process runs separately:

```bash
just worker-dev  # Development
docker compose up worker  # Production
```

## Frontend Architecture

### Template Hierarchy

```
base/skeleton.html.jinja         # Base layout
└── base/auth.html.jinja         # Requires authentication
    └── dashboard.html.jinja     # Specific page
```

### HTMX Patterns

**Partial Updates**:

```html
<div id="posts">
  <button
    hx-get="/posts?page=2"
    hx-target="#posts"
    hx-swap="beforeend">
    Load More
  </button>
</div>
```

**Form Submission**:

```html
<form hx-post="/comments" hx-target="#comments" hx-swap="afterbegin">
  <textarea name="content"></textarea>
  <button type="submit">Post Comment</button>
</form>
```

**Server Response**:

```python
@router.post("/comments")
async def create_comment(content: str):
    comment = await Comment(content=content).insert()
    return templates.TemplateResponse("comments/item.html.jinja", {
        "comment": comment
    })
```

### Asset Pipeline

**Development**:

```bash
bun dev  # Watch mode
```

Compiles:
- `assets/config.css` → `assets/statics/css/bundle.css`
- `assets/config.js` → `assets/statics/js/bundle.js`

**Production**:

```bash
bun build-prod
```

Minifies and optimizes for production.

## Configuration Management

**Location**: `src/vibetuner/config.py`

Pydantic Settings with environment variable support:

```python
class Settings(BaseSettings):
    # Automatic from .env or environment
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False

    # OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
```

## Deployment Architecture

### Docker Multi-Stage Build

```dockerfile
# Stage 1: Python dependencies
FROM python:3.11-slim as deps
COPY pyproject.toml .
RUN uv sync

# Stage 2: Application code
FROM deps as app
COPY src/ ./src/
COPY templates/ ./templates/

# Stage 3: Frontend assets
FROM node:20-slim as frontend
COPY package.json .
RUN bun install
COPY assets/ ./assets/
RUN bun build-prod

# Stage 4: Runtime
FROM app as runtime
COPY --from=frontend /app/assets/statics/ /app/assets/statics/
CMD ["granian", "--host", "0.0.0.0", "--port", "8000", "app.frontend:app"]
```

### Production Stack

```
┌──────────────┐
│ Load Balancer│
└──────┬───────┘
       │
       ├─────┬──────────┬──────────┐
       │     │          │          │
   ┌───▼─┐ ┌─▼──┐  ┌───▼─┐   ┌───▼─┐
   │App 1│ │App2│  │App 3│   │App 4│
   └───┬─┘ └─┬──┘  └───┬─┘   └───┬─┘
       │     │          │          │
       └─────┴─────┬────┴──────────┘
                   │
       ┌───────────┴────────────┐
       │                        │
   ┌───▼──────┐          ┌─────▼────┐
   │ MongoDB  │          │  Redis   │
   │(Replica) │          │ (Master) │
   └──────────┘          └──────────┘
```

## Scaling Considerations

### Horizontal Scaling

- Run multiple application instances
- Use Redis for session storage
- Load balance with Nginx/Caddy
- Database connection pooling

### Database Scaling

- MongoDB replica sets for high availability
- Read replicas for read-heavy workloads
- Sharding for very large datasets
- Indexes on frequently queried fields

### Caching Strategy

- Redis for session data
- Redis for rate limiting
- Redis for job queues
- Application-level caching for expensive queries

### Asset Delivery

- Serve static files from CDN
- Use cache headers appropriately
- Minify and compress assets
- Implement versioned URLs

## Security Architecture

### Authentication

- OAuth 2.0 with secure providers
- Magic links with time-limited tokens
- HTTP-only secure cookies
- CSRF protection with SameSite cookies

### Database

- Connection string authentication
- Network isolation (VPC)
- TLS/SSL connections
- Regular backups

### Application

- Environment-based secrets
- Input validation with Pydantic
- SQL injection protection (ODM)
- XSS protection (Jinja2 auto-escaping)
- HTTPS enforcement in production

## Monitoring Points

### Application

- Request/response times
- Error rates
- Active sessions
- Background job queue length

### Database

- Query performance
- Connection pool usage
- Disk usage
- Replica lag

### Infrastructure

- CPU/Memory usage
- Network throughput
- Disk I/O
- Container health

## Next Steps

- [Development Guide](development-guide.md) - Build features
- [Deployment](deployment.md) - Deploy to production
- [Tech Stack](tech-stack.md) - Technology choices
