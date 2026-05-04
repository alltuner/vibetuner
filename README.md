<p align="center">
  <img src="https://brand.alltuner.com/logos/vibetuner/horizontal.png" alt="Vibetuner" width="500">
</p>

<p align="center">
  <strong>Production-ready FastAPI scaffolding in seconds.</strong><br>
  Authentication, database, frontend, Docker, and CLI tools, pre-configured.
</p>

<p align="center">
  <a href="https://github.com/alltuner/vibetuner/tree/main/vibetuner-docs/docs">Docs</a> &middot;
  <a href="https://alltuner.com/sponsor">Sponsor</a>
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/vibetuner?color=5B2333" alt="PyPI">
  <img src="https://img.shields.io/npm/v/@alltuner/vibetuner?color=5B2333" alt="npm">
  <img src="https://img.shields.io/github/license/alltuner/vibetuner?color=5B2333" alt="License">
  <img src="https://img.shields.io/github/stars/alltuner/vibetuner?color=5B2333" alt="Stars">
</p>

---

## Get Started

### Option 1: just add the package

```bash
uv add vibetuner
vibetuner run dev
# → working app at http://localhost:8000
```

### Option 2: full project scaffolding

```bash
uvx vibetuner scaffold new my-project
cd my-project && just dev
# → full application with Docker, CI/CD, and more
```

What you get out of the package alone:

- FastAPI backend with async support.
- OAuth + magic-link authentication.
- Default templates and styles.
- Hot reload in development.
- Auto-discovery of routes, models, and tasks.

What scaffolding adds:

- Flexible database: MongoDB (Beanie) or SQL (SQLModel/SQLAlchemy).
- HTMX reactive frontend.
- Tailwind CSS + DaisyUI styling.
- Docker dev/prod environments.
- Background jobs with Redis (optional).
- i18n support.
- CI/CD workflows.

---

## What is Vibetuner?

Vibetuner is the scaffolding All Tuner Labs uses to spin up new web applications. It packages a FastAPI backend, an HTMX/Tailwind frontend, OAuth + magic-link auth, optional MongoDB or SQL persistence, and Docker for both dev and production into a single installable framework. The scaffolder generates the project; the framework runs it.

### Core principles

- **Simplicity** — minimal boilerplate, clear conventions, obvious patterns.
- **Speed** — sub-second hot reload, one command to start.
- **Modern stack** — async-first, current stable versions.
- **Assistant-friendly** — works well with Claude, Cursor, and other coding agents.

## Tech stack

### Backend

- **[FastAPI](https://fastapi.tiangolo.com/)** — async web framework.
- **[Granian](https://github.com/emmett-framework/granian)** — Rust-based ASGI server.

### Database (pick what fits)

- **[MongoDB](https://www.mongodb.com/) + [Beanie ODM](https://beanie-odm.dev/)** — document database (optional).
- **[SQLModel](https://sqlmodel.tiangolo.com/) / [SQLAlchemy](https://www.sqlalchemy.org/)** — PostgreSQL, MySQL, MariaDB, SQLite (optional).
- **[Redis](https://redis.io/) + [Streaq](https://github.com/tastyware/streaq)** — caching and background jobs (optional).

### Frontend

- **[HTMX](https://htmx.org/)** — dynamic HTML without a separate JS build step.
- **[Tailwind CSS](https://tailwindcss.com/)** — utility-first CSS framework.
- **[DaisyUI](https://daisyui.com/)** — Tailwind component set.
- **[Jinja2](https://jinja.palletsprojects.com/)** — template engine with i18n.

### DevOps

- **[Docker](https://www.docker.com/)** — multi-stage builds for dev/prod.
- **[uv](https://docs.astral.sh/uv/)** — Python package management.
- **[bun](https://bun.sh/)** — JavaScript tooling.
- **[just](https://just.systems/)** — command runner.

## Development

### Local

```bash
just local-all        # server + assets with auto-port (recommended)
```

### Docker

```bash
just dev              # all-in-one with hot reload
just worker-dev       # background worker (if enabled)
```

### Common commands

```bash
just install-deps     # install dependencies from lockfiles
just format           # format code
just test-build-prod  # test production build locally
```

## Project structure

The `vibetuner` package is installed as a dependency. Your application code lives under `src/` in a directory named after your project slug (shown as `app` below):

```text
my-app/
├── src/app/                # your application code (you create this)
│   ├── config.py           # app configuration (optional)
│   ├── cli/                # your CLI commands (auto-discovered)
│   ├── frontend/           # your web routes
│   │   └── routes/         # (auto-discovered)
│   ├── models/             # your database models (auto-discovered)
│   ├── services/           # your business logic
│   └── tasks/              # your background jobs (auto-discovered)
├── templates/              # Jinja2 templates
│   ├── frontend/           # web templates (override defaults)
│   ├── email/              # email templates
│   └── markdown/           # markdown templates
├── assets/statics/         # static files (css, js, img, fonts)
├── locales/                # i18n translation files
└── Dockerfile              # production deployment
```

The framework auto-discovers code from your package directory. Scaffolded projects use `src/<project_slug>/`; non-scaffolded projects can use any structure.

## Authentication

Built-in, zero config:

- **OAuth** — Google, GitHub, and more via Authlib.
- **Magic links** — passwordless email authentication.
- **Sessions** — secure cookie-based sessions.
- **Extensible** — add providers or custom auth easily.

## Internationalization

```bash
just extract-translations    # extract strings
just compile-locales         # compile translations
```

```jinja
{% trans %}Welcome to {{ app_name }}{% endtrans %}
```

## Deployment

### Docker production

```bash
just test-build-prod    # test locally
just release            # build and push
```

### Configuration

Environment variables via `.env`:

```bash
# MongoDB (optional)
MONGODB_URL=mongodb://localhost:27017/mydb

# SQL database (optional) — PostgreSQL, MySQL, or SQLite
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
# DATABASE_URL=sqlite+aiosqlite:///./data.db

# Redis for background jobs (optional)
REDIS_URL=redis://localhost:6379

SECRET_KEY=your-secret-key
```

## Updating projects

Update an existing project to the latest template:

```bash
cd my-app
vibetuner scaffold update
```

## Documentation

- **[Development guide](vibetuner-docs/docs/development-guide.md)** — daily workflow for generated projects.
- **[CLI reference](vibetuner-docs/docs/cli-reference.md)** — `vibetuner scaffold` and `vibetuner run` usage.
- **[Scaffolding reference](vibetuner-docs/docs/scaffolding.md)** — Copier prompts and update commands.
- **[Changelog](vibetuner-docs/docs/changelog.md)** — version history and release notes.
- **[Contributing](./CONTRIBUTING.md)** — contribution guidelines.
- **[Assistant guidance](./CLAUDE.md)** — tips for AI coding partners.

## Packages

Vibetuner ships as three coordinated packages, version-locked and tested together:

| Package | Description | Registry |
|---|---|---|
| [`vibetuner`](https://pypi.org/project/vibetuner/) | Python framework | PyPI |
| [`@alltuner/vibetuner`](https://www.npmjs.com/package/@alltuner/vibetuner) | Frontend dependencies | npm |
| Scaffolding template | Copier template | GitHub |

## License

[MIT](LICENSE)

## Support the project

Vibetuner is an open source project built by [David Poblador i Garcia](https://davidpoblador.com/) through [All Tuner Labs](https://www.alltuner.com/).

If this project was useful to you, [consider supporting its development](https://alltuner.com/sponsor).

---

<p align="center">
  Built by <a href="https://davidpoblador.com">David Poblador i Garcia</a> with the support of <a href="https://alltuner.com">All Tuner Labs</a>.<br>
  Made with ❤️ in Poblenou, Barcelona.
</p>
