# Vibetuner

**Production-ready FastAPI + MongoDB + HTMX project scaffolding**

Vibetuner is a comprehensive project scaffolding tool that generates modern, full-stack web applications using All Tuner Labs' blessed technology stack. It provides everything you need to build, deploy, and maintain production-ready web applications.

## Features

- 🚀 **Complete Stack**: FastAPI, MongoDB (Beanie ODM), HTMX, Tailwind CSS, DaisyUI
- 🔐 **Built-in Auth**: OAuth providers + passwordless magic links
- 🎨 **Modern Frontend**: HTMX for reactivity, Tailwind CSS + DaisyUI for styling
- 📦 **Background Jobs**: Optional Redis + Streaq task queue
- 🌍 **i18n Ready**: Full internationalization support with babel
- 🐳 **Docker-first**: Multi-stage builds, dev/prod compose files
- 🛠️ **Developer Experience**: Hot reload, type checking, formatting, linting
- 📝 **CLI Tools**: Custom commands via Typer
- ⚡ **Performance**: Async-first with Granian ASGI server

## Quick Start

### Installation

```bash
# Using uvx (recommended - no installation needed)
uvx vibetuner scaffold new my-project

# Or install globally
uv tool install vibetuner
vibetuner scaffold new my-project
```

### Interactive Setup

The scaffold command will prompt you for:
- Project name and description
- Author/company information
- Python version (3.11-3.14)
- Supported languages for i18n
- Optional features (job queue, deployment configs)

### Non-Interactive Mode

```bash
# Use defaults for quick start
uvx vibetuner scaffold new my-project --defaults

# Override specific values
uvx vibetuner scaffold new my-project --defaults \
  --data project_name="My App" \
  --data author_name="Your Name" \
  --data python_version="3.13"
```

## Generated Project Structure

```
my-project/
├── src/
│   ├── vibetuner/          # Core framework (immutable)
│   │   ├── frontend/      # Web routes, auth, middleware
│   │   ├── models/        # User, OAuth, core models
│   │   ├── services/      # Email, storage services
│   │   ├── tasks/         # Background job infrastructure
│   │   └── cli/           # CLI framework
│   └── app/               # Your application code
│       ├── frontend/      # Your routes
│       ├── models/        # Your models
│       ├── services/      # Your services
│       ├── tasks/         # Your background jobs
│       └── cli/           # Your CLI commands
├── templates/
│   ├── frontend/          # Jinja2 templates
│   ├── email/             # Email templates
│   └── markdown/          # Markdown templates
├── assets/
│   └── statics/           # CSS, JS, images
├── locales/               # Translation files
├── Dockerfile             # Multi-stage Docker build
├── compose.dev.yml        # Development environment
├── compose.prod.yml       # Production environment
└── justfile               # Development commands
```

## Development

### Local Development

```bash
cd my-project

# Terminal 1: Frontend asset building
bun dev

# Terminal 2: Backend server with hot reload
just local-dev
```

### Docker Development

```bash
just dev              # All-in-one with hot reload
just worker-dev       # Background worker (if enabled)
```

### Common Commands

```bash
# Dependencies
just sync             # Sync Python + JS dependencies
uv add package        # Add Python package
bun add package       # Add JS package

# Code Quality
ruff format .         # Format code
ruff check --fix .    # Fix linting issues
just format           # Format all (Python + templates)

# Localization
just extract-translations   # Extract i18n strings
just compile-locales        # Compile translations

# Version & Release
just bump-patch      # Bump patch version
just bump-minor      # Bump minor version
just pr              # Create pull request
```

## Tech Stack

### Backend
- **FastAPI** (0.121+): Modern, fast web framework
- **MongoDB** with **Beanie ODM**: Document database with Pydantic models
- **Granian**: High-performance ASGI server
- **Redis** (optional): Caching and task queue backend
- **Streaq** (optional): Background job processing

### Frontend
- **HTMX** (2.0+): Dynamic HTML without complex JavaScript
- **Tailwind CSS** (4.1+): Utility-first CSS framework
- **DaisyUI** (5.4+): Beautiful Tailwind components
- **Jinja2**: Template engine with i18n support

### Developer Tools
- **uv**: Fast Python package management
- **bun**: Fast JavaScript package management
- **Ruff**: Fast Python linter and formatter
- **djlint**: Template linter and formatter
- **just**: Command runner (like make, but better)
- **Typer**: CLI framework

## Authentication

Built-in authentication supports:

- **OAuth Providers**: Google, GitHub, and more via Authlib
- **Magic Links**: Passwordless email authentication
- **Session Management**: Secure cookie-based sessions
- **User Models**: Extensible user and OAuth account models

## Background Jobs (Optional)

When enabled, includes:

- **Streaq**: Modern async task queue for Python
- **Redis**: Fast in-memory storage
- **Web UI**: Built-in task monitoring dashboard
- **Retry Logic**: Automatic retries with backoff
- **Task Scheduling**: Cron-like task scheduling

## Internationalization

Full i18n support with:

- **Babel**: Industry-standard i18n toolkit
- **Message Extraction**: Automatic string extraction
- **Template Support**: `{% trans %}` tags in Jinja2
- **Language Selection**: Automatic language detection
- **Fallbacks**: Graceful fallback to default language

## Deployment

### Docker Production

```bash
just test-build-prod    # Test production build locally
just release            # Build and push to registry
```

### Configuration

Environment variables via `.env`:

```bash
# Database
DATABASE_URL=mongodb://localhost:27017/mydb

# Redis (if job queue enabled)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here

# AWS (for email/storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1

# OAuth (optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
```

## Packages

Vibetuner consists of three packages:

1. **vibetuner** (Python): Core framework and blessed dependencies
2. **@alltuner/vibetuner** (JavaScript): Frontend build dependencies
3. **scaffolding template**: Copier template for project generation

All packages are version-locked and tested together to ensure compatibility.

## Philosophy

Vibetuner is designed around these principles:

- **Convention over Configuration**: Sensible defaults, minimal boilerplate
- **Batteries Included**: Everything you need out of the box
- **Separation of Concerns**: Core framework vs application code
- **Developer Experience**: Fast iteration, great tooling
- **Production Ready**: Docker, health checks, monitoring
- **Modern Stack**: Latest stable versions, async-first

## Updating Projects

Update an existing project to the latest template version:

```bash
cd my-project
vibetuner scaffold update

# Or from any directory
vibetuner scaffold update /path/to/my-project
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](./LICENSE) for details.

Copyright (c) 2025 All Tuner Labs, S.L.

## Links

- **Documentation**: https://github.com/alltuner/vibetuner
- **Issues**: https://github.com/alltuner/vibetuner/issues
- **PyPI**: https://pypi.org/project/vibetuner/
- **npm**: https://www.npmjs.com/package/@alltuner/vibetuner

## Credits

Created and maintained by [All Tuner Labs, S.L.](https://alltuner.com)

Main contributor: David Poblador ([@davidpoblador](https://github.com/davidpoblador))
