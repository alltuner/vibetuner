# Tech Stack

Understanding the technologies behind Vibetuner.

## Overview

Vibetuner combines modern, production-tested technologies into a cohesive stack
optimized for rapid development and deployment.

## Backend Stack

### FastAPI

**Why:** Modern, fast, async-first Python web framework.

- Automatic API documentation (OpenAPI/Swagger)
- Async/await support throughout
- Pydantic integration for validation
- Type hints and IDE support
- High performance (comparable to Node.js/Go)
**Links:**
- [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- [GitHub](https://github.com/tiangolo/fastapi)

## Database Options

Vibetuner supports multiple database backends. All are optional - choose what fits your project.

### MongoDB + Beanie ODM

**Why:** Flexible document database for rapid prototyping.

- Schema flexibility during rapid development
- Pydantic models are database models
- Type-safe async operations
- Automatic validation
- Horizontal scaling with sharding

**Links:**

- [mongodb.com](https://www.mongodb.com/)
- [beanie-odm.dev](https://beanie-odm.dev/)

### SQLModel + SQLAlchemy

**Why:** SQL databases when you need relational data.

- PostgreSQL, MySQL, MariaDB, SQLite support
- Pydantic + SQLAlchemy combined
- Type-safe async operations
- Full SQL power when needed
- CLI command: `vibetuner db create-schema`

**Links:**

- [sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com/)
- [sqlalchemy.org](https://www.sqlalchemy.org/)

### Granian

**Why:** High-performance ASGI server written in Rust.

- Faster than Uvicorn/Gunicorn
- Lower memory footprint
- Built-in process management
- Hot reload in development
**Links:**
- [GitHub](https://github.com/emmett-framework/granian)

### Pydantic

**Why:** Data validation using Python type annotations.

- Runtime type checking
- JSON Schema generation
- Settings management
- Clear error messages
**Links:**
- [docs.pydantic.dev](https://docs.pydantic.dev/)
- [GitHub](https://github.com/pydantic/pydantic)

## Frontend Stack

### HTMX

**Why:** Interactivity without complex JavaScript.

- Server-rendered HTML with dynamic updates
- Progressive enhancement
- Minimal client-side complexity
- Works with any backend
- Small footprint (~14kb)
**Links:**
- [htmx.org](https://htmx.org/)
- [GitHub](https://github.com/bigskysoftware/htmx)

### Tailwind CSS

**Why:** Utility-first CSS framework.

- Rapid UI development
- No naming conventions needed
- Automatic purging of unused CSS
- Responsive design made simple
- Customizable design system
**Links:**
- [tailwindcss.com](https://tailwindcss.com/)
- [GitHub](https://github.com/tailwindlabs/tailwindcss)

### DaisyUI

**Why:** Beautiful Tailwind CSS components.

- Pre-built components
- Theming support
- No JavaScript required
- Semantic class names
- Accessibility built-in
**Links:**
- [daisyui.com](https://daisyui.com/)
- [GitHub](https://github.com/saadeghi/daisyui)

### Jinja2

**Why:** Powerful template engine for Python.

- Template inheritance
- Macros for reusable components
- Filters and functions
- i18n integration
- Sandboxed execution
**Links:**
- [jinja.palletsprojects.com](https://jinja.palletsprojects.com/)
- [GitHub](https://github.com/pallets/jinja)

## Background Jobs (Optional)

### Redis

**Why:** In-memory data store for caching and queues.

- Extremely fast (~100k ops/sec)
- Multiple data structures
- Pub/sub messaging
- Persistence options
- Simple to deploy
**Links:**
- [redis.io](https://redis.io/)
- [GitHub](https://github.com/redis/redis)

### Streaq

**Why:** Simple, reliable background job processing.

- Built on Redis
- Async/await support
- Job scheduling
- Retry logic
- Web UI for monitoring
**Links:**
- [GitHub](https://github.com/tastyware/streaq)

## Framework Patterns

### CRUD Route Factory

**Why:** Eliminate boilerplate for standard data endpoints.

- Generate list/create/read/update/delete routes from a Beanie Document
- Built-in pagination, sorting, filtering, and text search
- Pre/post hooks for custom logic (validation, side effects)
- Custom request/response schemas
- Field selection for partial responses

### Server-Sent Events (SSE)

**Why:** Real-time updates without WebSocket complexity.

- Channel-based pub/sub with `broadcast()` / `sse_endpoint()`
- In-process asyncio queues for single-worker mode
- Redis pub/sub bridge for multi-worker deployments
- Render Jinja2 templates directly as SSE payloads
- Automatic keepalive for long-lived connections
- Works natively with HTMX built-in SSE support (no extension needed in v4)

### Runtime Configuration

**Why:** Change app behavior without redeployment.

- Layered resolution: runtime overrides > MongoDB > code defaults
- `@config_value` decorator and `ConfigGroup` class for type-safe access
- Cache with configurable TTL to avoid per-request DB queries
- FastAPI dependency (`get_runtime_config`) for route injection

### Testing Framework

**Why:** Test vibetuner apps without external services.

- `vibetuner_client` — async HTTP client with full middleware stack
- `vibetuner_db` — temporary MongoDB with auto-teardown
- `mock_auth` — patch authentication without sessions or cookies
- `mock_tasks` — record background task enqueue calls without Redis
- `override_config` — temporarily override runtime config values

### Health Monitoring

**Why:** Production observability out of the box.

- `/health/ping` — fast liveness probe
- `/health?detailed=true` — service-level latency checks
- `/health/ready` — readiness probe for orchestrators
- Checks MongoDB, Redis, S3/R2, and email connectivity
- Reports version, uptime, and instance identity

### Robust Task Processing

**Why:** Reliable background jobs in production.

- `@robust_task` decorator with exponential backoff retries
- Dead letter collection in MongoDB for failed tasks
- Optional failure callback (sync or async)
- Works alongside standard `@worker.task()` tasks

### Project Diagnostics

**Why:** Fast troubleshooting for new and existing projects.

- `vibetuner doctor` CLI command
- Validates project structure, env vars, service connectivity
- Checks models, templates, dependencies, and port availability
- Rich console output with actionable fix instructions

## Development Tools

### uv

**Why:** Extremely fast Python package manager.

- 10-100x faster than pip
- Reliable dependency resolution
- Compatible with pip/requirements.txt
- Built in Rust
**Links:**
- [docs.astral.sh/uv](https://docs.astral.sh/uv/)
- [GitHub](https://github.com/astral-sh/uv)

### bun

**Why:** Fast all-in-one JavaScript runtime and toolkit.

- 2-10x faster than npm/pnpm
- Built-in bundler, transpiler, test runner
- Drop-in Node.js replacement
- Native TypeScript support
**Links:**
- [bun.sh](https://bun.sh/)
- [GitHub](https://github.com/oven-sh/bun)

### just

**Why:** Command runner (better Make).

- Simple syntax
- Cross-platform
- Environment variable support
- Recipe dependencies
**Links:**
- [just.systems](https://just.systems/)
- [GitHub](https://github.com/casey/just)

### Ruff

**Why:** Extremely fast Python linter and formatter.

- 10-100x faster than Flake8/Black
- Drop-in replacement
- Comprehensive rules
- Automatic fixes
**Links:**
- [docs.astral.sh/ruff](https://docs.astral.sh/ruff/)
- [GitHub](https://github.com/astral-sh/ruff)

## Authentication

### Authlib

**Why:** Comprehensive OAuth library.

- Multiple OAuth providers
- OAuth 1.0/2.0 support
- OpenID Connect
- JWT handling
- Well-maintained
**Links:**
- [authlib.org](https://authlib.org/)
- [GitHub](https://github.com/lepture/authlib)

## Deployment

### Docker

**Why:** Containerization for consistent deployments.

- Same environment everywhere
- Dependency isolation
- Easy scaling
- Production-ready
**Links:**
- [docker.com](https://www.docker.com/)
- [Documentation](https://docs.docker.com/)

### Copier

**Why:** Template-based project scaffolding.

- Update existing projects
- Conditional templating
- Git integration
- Jinja2 templates
**Links:**
- [copier.readthedocs.io](https://copier.readthedocs.io/)
- [GitHub](https://github.com/copier-org/copier)

## Why These Choices?

### Speed of Development

Every tool is chosen for rapid iteration:

- **FastAPI**: Auto-generated docs, type hints
- **HTMX**: No build step, server-side logic
- **Tailwind**: Style without leaving HTML
- **uv/bun**: Instant dependency installation

### Simplicity

Less complexity means faster development:

- **HTMX over React**: No state management, no build complexity
- **Flexible databases**: MongoDB for documents, SQL for relations - your choice
- **DaisyUI**: Pre-built components without JavaScript
- **Pydantic everywhere**: Models, validation, settings - one pattern

### Modern & Maintained

All tools are actively maintained with modern approaches:

- Async-first (FastAPI, Beanie, Streaq)
- Type-safe (Pydantic, Python 3.11+)
- Performance-focused (Granian, uv, bun, Ruff)
- Rust-powered tools for speed (uv, Ruff, Granian)

### Production-Ready

Not just for prototypes:

- **MongoDB/PostgreSQL**: Powers large-scale applications
- **FastAPI**: Used by Microsoft, Uber, Netflix
- **Docker**: Industry standard deployment
- **Redis**: Battle-tested caching and queues

### AI-Friendly

Works great with coding assistants:

- Clear conventions and patterns
- Comprehensive type hints
- Well-documented stack
- Predictable project structure

## Version Requirements

- **Python**: 3.11+ (3.14 recommended)
- **MongoDB**: 5.0+
- **Redis**: 6.0+ (if using background jobs)
- **Node.js**: Not required (bun replaces it)

## Next Steps

- [Quick Start](quick-start.md) - Start building
- [Architecture](architecture.md) - System design
- [Development Guide](development-guide.md) - Daily workflow
