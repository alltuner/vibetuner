# Vibetuner

## Production-ready FastAPI web application scaffolding in seconds

Vibetuner generates full-stack web applications with authentication, database,
frontend, Docker deployment, and CLI tools pre-configured.

Built by [All Tuner Labs](https://www.alltuner.com) for rapid iteration and modern development.

## ✨ What You Get

### Option 1: Just add the package

```bash
uv add vibetuner
vibetuner run dev
# → Working app at http://localhost:8000
```

### Option 2: Full project scaffolding

```bash
uvx vibetuner scaffold new my-project
cd my-project && just dev
# → Full application with Docker, CI/CD, and more
```

**What vibetuner provides immediately (no scaffolding needed)**:

- ✅ FastAPI backend with async support
- ✅ OAuth + magic link authentication
- ✅ Default templates and styles
- ✅ Hot reload in development
- ✅ Auto-discovery of your routes, models, and tasks

**What scaffolding adds**:

- ✅ **Flexible database**: MongoDB (Beanie) or SQL (SQLModel/SQLAlchemy)
- ✅ HTMX reactive frontend
- ✅ Tailwind CSS + DaisyUI styling
- ✅ Docker dev/prod environments
- ✅ Background jobs with Redis (optional)
- ✅ i18n support
- ✅ CI/CD workflows

## 🚀 Quick Start

### Installation

**No installation needed** - use `uvx`:

```bash
uvx vibetuner scaffold new my-app
```

Or install globally:

```bash
uv tool install vibetuner
vibetuner scaffold new my-app
```

### Your First Project

```bash
# Create project (interactive)
uvx vibetuner scaffold new my-app

# Or skip questions with defaults
uvx vibetuner scaffold new my-app --defaults

# Start developing
cd my-app
just dev              # Docker mode with hot reload
```

Visit `http://localhost:8000` - your app is running!

## 🎯 Core Principles

**Born from real needs** at [All Tuner Labs](https://alltuner.com) when spawning new projects:

- **Simplicity**: Minimal boilerplate, clear conventions, obvious patterns
- **Speed**: Sub-second hot reload, one command to start, fast iteration
- **Modern Stack**: Latest stable versions, async-first, production-tested
- **Assistant-Friendly**: Works great with Claude, Cursor, and other coding AI

## 📦 Tech Stack

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

### Why These Choices?

**FastAPI**: Async-first, automatic API docs, Pydantic validation, type hints everywhere.

**Flexible databases**: Start with MongoDB for rapid prototyping, or use PostgreSQL/MySQL/SQLite
with SQLModel for relational data. Both are optional - use what fits your project.

**HTMX over React/Vue**: Simplicity wins. Server-rendered HTML with sprinkles
of interactivity. Less complexity, faster development, easier to reason about.

**Tailwind + DaisyUI**: Utility-first CSS is fast once you learn it. DaisyUI
provides components without JavaScript bloat.

**Docker-first**: Consistent environments, easy deployment, no "works on my
machine" problems.

**uv + bun**: Speed matters. Both are order-of-magnitude faster than pip/npm.
Fast lockfiles, fast installs, fast everything.

## 💻 Development

### Local Development

```bash
just local-all        # Runs server + assets with auto-port (recommended)
```

### Docker Development

```bash
just dev              # All-in-one with hot reload
just worker-dev       # Background worker (if enabled)
```

### Common Commands

```bash
just install-deps     # Install dependencies from lockfiles
just format           # Format code
just test-build-prod  # Test production build locally
```

## 🏗️ Project Structure

The `vibetuner` package is installed as a dependency. Your application code lives under `src/`
in a directory named after your project slug (shown as `app` below):

```text
my-app/
├── src/app/                # Your application code (you create this)
│   ├── config.py           # App configuration (optional)
│   ├── cli/                # Your CLI commands (auto-discovered)
│   ├── frontend/           # Your web routes
│   │   └── routes/        # (auto-discovered)
│   ├── models/             # Your database models (auto-discovered)
│   ├── services/           # Your business logic
│   └── tasks/              # Your background jobs (auto-discovered)
├── templates/              # Jinja2 templates
│   ├── frontend/           # Web templates (override defaults)
│   ├── email/              # Email templates
│   └── markdown/           # Markdown templates
├── assets/statics/         # Static files (css, js, img, fonts)
├── locales/                # i18n translation files
└── Dockerfile              # Production deployment
```

**vibetuner** (installed package) handles auth, database, email, auto-discovery, and more.
Your code goes in `src/<your_package>/` (scaffolded projects). No boilerplate `__init__.py`
files needed.

**Flexible project structures**: The framework auto-discovers code from your package directory.
Scaffolded projects use `src/<project_slug>/`; non-scaffolded projects can use any structure.

## 🔐 Authentication

Built-in authentication with zero config:

- **OAuth**: Google, GitHub, and more via Authlib
- **Magic Links**: Passwordless email authentication
- **Sessions**: Secure cookie-based sessions
- **Extensible**: Add providers or custom auth easily

## 🌍 Internationalization

Full i18n support:

```bash
just extract-translations    # Extract strings
just compile-locales         # Compile translations
```

```jinja
{% trans %}Welcome to {{ app_name }}{% endtrans %}
```

## 🐳 Deployment

### Docker Production

```bash
just test-build-prod    # Test locally
just release            # Build and push
```

### Configuration

Environment variables via `.env`:

```bash
# MongoDB (optional)
MONGODB_URL=mongodb://localhost:27017/mydb

# SQL database (optional) - PostgreSQL, MySQL, or SQLite
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
# DATABASE_URL=sqlite+aiosqlite:///./data.db

# Redis for background jobs (optional)
REDIS_URL=redis://localhost:6379

SECRET_KEY=your-secret-key
```

## 📚 Documentation

- **[Development Guide](vibetuner-docs/docs/development-guide.md)** – Daily workflow for generated projects
- **[CLI Reference](vibetuner-docs/docs/cli-reference.md)** – Usage for `vibetuner scaffold` and `vibetuner run`
- **[Scaffolding Reference](vibetuner-docs/docs/scaffolding.md)** – Copier prompts and update commands
- **[Changelog](vibetuner-docs/docs/changelog.md)** – Version history and release notes
- **[Contributing](./CONTRIBUTING.md)** – Contribution guidelines
- **[Assistant Guidance](./CLAUDE.md)** – Tips for AI coding partners

## 📦 Packages

Vibetuner consists of three packages:

| Package | Description | Published |
|---------|-------------|-----------|
| [`vibetuner`](https://pypi.org/project/vibetuner/) | Python framework | PyPI |
| [`@alltuner/vibetuner`](https://www.npmjs.com/package/@alltuner/vibetuner) | Frontend dependencies | npm |
| Scaffolding template | Copier template | GitHub |

All version-locked and tested together.

## 🔄 Updating Projects

Update existing projects to the latest template:

```bash
cd my-app
vibetuner scaffold update
```

## 🤝 Contributing

We welcome contributions that align with our core principles! See [CONTRIBUTING.md](./CONTRIBUTING.md).

Built for All Tuner Labs' internal needs, shared publicly because it might help you too.

## 📄 License

MIT License - Copyright (c) 2026 All Tuner Labs, S.L.

See [LICENSE](./LICENSE) for details.

## 🔗 Links

- **Repository**: <https://github.com/alltuner/vibetuner>
- **Changelog**: <https://github.com/alltuner/vibetuner/blob/main/CHANGELOG.md>
- **Issues**: <https://github.com/alltuner/vibetuner/issues>
- **PyPI**: <https://pypi.org/project/vibetuner/>
- **npm**: <https://www.npmjs.com/package/@alltuner/vibetuner>

## 👨‍💻 Credits

Created and maintained by [All Tuner Labs, S.L.](https://alltuner.com) and
David Poblador i Garcia ([@davidpoblador](https://github.com/davidpoblador) |
[davidpoblador.com](https://davidpoblador.com/))

## Support the project

Vibetuner is an open source project built by [David Poblador i Garcia](https://davidpoblador.com/) through [All Tuner Labs](https://www.alltuner.com/).

If this project helped you ship faster or prototype with confidence, consider supporting its development.

❤️ **Sponsor development**
https://github.com/sponsors/alltuner

☕ **One-time support**
https://buymeacoffee.com/alltuner

Your support helps fund the continued development of Vibetuner and other open source developer tools such as [Factory Floor](https://github.com/alltuner/factoryfloor).

---

Made with ❤️ for rapid prototyping and production deployments

![All Tuner Labs](https://alltuner.com/statics/img/vibetuner-horizontal-logo.png)
