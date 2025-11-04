# Tech Stack

Understanding the technologies behind Vibetuner.

## Overview

Vibetuner combines modern, production-tested technologies into a cohesive stack optimized for rapid development and deployment.

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

### MongoDB

**Why:** Flexible document database that scales with your data.

- Schema flexibility during rapid development
- Powerful query language
- Horizontal scaling with sharding
- Change streams for real-time features
- ACID transactions support

**Links:**
- [mongodb.com](https://www.mongodb.com/)
- [Documentation](https://docs.mongodb.com/)

### Beanie ODM

**Why:** Async MongoDB ODM built on Pydantic.

- Pydantic models are database models
- Type-safe database operations
- Automatic validation
- Migration support
- Query builder with type hints

**Links:**
- [beanie-odm.dev](https://beanie-odm.dev/)
- [GitHub](https://github.com/roman-right/beanie)

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

### djlint

**Why:** Template linter and formatter.

- Formats Jinja2/Django templates
- Finds common errors
- Enforces consistency

**Links:**
- [djlint.com](https://djlint.com/)
- [GitHub](https://github.com/Riverside-Healthcare/djLint)

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
- **MongoDB**: Flexible schema, no migrations during prototyping
- **DaisyUI**: Pre-built components without JavaScript
- **Beanie**: Database models are Pydantic models

### Modern & Maintained

All tools are actively maintained with modern approaches:

- Async-first (FastAPI, Beanie, Streaq)
- Type-safe (Pydantic, Python 3.11+)
- Performance-focused (Granian, uv, bun, Ruff)
- Rust-powered tools for speed (uv, Ruff, Granian)

### Production-Ready

Not just for prototypes:

- **MongoDB**: Powers large-scale applications
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

- **Python**: 3.11+
- **MongoDB**: 5.0+
- **Redis**: 6.0+ (if using background jobs)
- **Node.js**: Not required (bun replaces it)

## Next Steps

- [Quick Start](quick-start.md) - Start building
- [Architecture](architecture.md) - System design
- [Development Guide](development-guide.md) - Daily workflow
