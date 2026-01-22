# Vibetuner

## Production-ready FastAPI Web Application Scaffolding in Seconds

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
Vibetuner generates full-stack web applications with authentication, database,
frontend, Docker deployment, and CLI tools pre-configured. Built by
[All Tuner Labs](https://alltuner.com) for rapid iteration and modern development.

## What You Get

```bash
uvx vibetuner scaffold new my-project
cd my-project && just dev
# → Full application running at http://localhost:8000
```

### In 30 Seconds You Have

- ✅ FastAPI backend with async support
- ✅ **Flexible database**: MongoDB (Beanie) or SQL (SQLModel/SQLAlchemy)
- ✅ OAuth + magic link authentication
- ✅ HTMX reactive frontend
- ✅ Tailwind CSS + DaisyUI styling
- ✅ Docker dev/prod environments
- ✅ Background jobs with Redis (optional)
- ✅ i18n support
- ✅ Hot reload for everything

## Core Principles

Born from real needs at [All Tuner Labs](https://alltuner.com) when spawning new
projects:

- **Simplicity**: Minimal boilerplate, clear conventions, obvious patterns
- **Speed**: Sub-second hot reload, one command to start, fast iteration
- **Modern Stack**: Latest stable versions, async-first, production-tested
- **Assistant-Friendly**: Works great with Claude, Cursor, and other coding AI

## Quick Links

- **[Quick Start](quick-start.md)** - Get started in 5 minutes
- **[Development Guide](development-guide.md)** - Daily development workflow
- **[Tech Stack](tech-stack.md)** - Technologies and why we chose them
- **[CLI Reference](cli-reference.md)** - Command-line usage for `vibetuner`
- **[Scaffolding Reference](scaffolding.md)** - Template prompts and update workflow
- **[Contributing](contributing.md)** - Help improve Vibetuner

## Tech Stack

### Backend

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern async web framework
- **[Granian](https://github.com/emmett-framework/granian)** - High-performance ASGI server

### Database (choose your stack)

- **[MongoDB](https://www.mongodb.com/)** + **[Beanie ODM](https://beanie-odm.dev/)** - Document database (optional)
- **[SQLModel](https://sqlmodel.tiangolo.com/)** / **[SQLAlchemy](https://www.sqlalchemy.org/)** - SQL databases: PostgreSQL, MySQL, MariaDB, SQLite (optional)
- **[Redis](https://redis.io/)** + **[Streaq](https://github.com/tastyware/streaq)** - Caching and background jobs (optional)

### Frontend

- **[HTMX](https://htmx.org/)** - Dynamic HTML without complex JavaScript
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[DaisyUI](https://daisyui.com/)** - Beautiful Tailwind components
- **[Jinja2](https://jinja.palletsprojects.com/)** - Template engine with i18n

### DevOps

- **[Docker](https://www.docker.com/)** - Multi-stage builds for dev/prod
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package management
- **[bun](https://bun.sh/)** - Fast JavaScript tooling
- **[just](https://just.systems/)** - Command runner

## Project Structure

Generated projects separate framework code from your code:

```text
my-app/
├── src/app/                # Your code (edit freely)
│   ├── frontend/routes/    # Your HTTP routes
│   ├── models/             # Your database models
│   └── services/           # Your business logic
├── templates/              # Jinja2 templates
└── Dockerfile              # Production deployment
```

The `vibetuner` framework (auth, database, core services) is installed as a package dependency.

## Community

- **GitHub**: [alltuner/vibetuner](https://github.com/alltuner/vibetuner)
- **Issues**: [Report bugs or request features](https://github.com/alltuner/vibetuner/issues)
- **PyPI**: [vibetuner](https://pypi.org/project/vibetuner/)
- **npm**: [@alltuner/vibetuner](https://www.npmjs.com/package/@alltuner/vibetuner)

## License

MIT License - Copyright (c) 2025 All Tuner Labs, S.L.
Created by David Poblador i Garcia ([@davidpoblador](https://github.com/davidpoblador) | [davidpoblador.com](https://davidpoblador.com/))
