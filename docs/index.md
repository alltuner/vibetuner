# Vibetuner

**Production-ready FastAPI + MongoDB + HTMX project scaffolding in seconds**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Vibetuner generates full-stack web applications with authentication, database, frontend, Docker deployment, and CLI tools pre-configured. Built by [All Tuner Labs](https://alltuner.com) for rapid iteration and modern development.

## What You Get

```bash
uvx vibetuner scaffold new my-project
cd my-project && just dev
# → Full application running at http://localhost:8000
```

**In 30 seconds you have:**

- ✅ FastAPI backend with async support
- ✅ MongoDB with Beanie ODM
- ✅ OAuth + magic link authentication
- ✅ HTMX reactive frontend
- ✅ Tailwind CSS + DaisyUI styling
- ✅ Docker dev/prod environments
- ✅ Background jobs (optional)
- ✅ i18n support
- ✅ Hot reload for everything

## Core Principles

**Born from real needs** at [All Tuner Labs](https://alltuner.com) when spawning new projects:

- **Simplicity**: Minimal boilerplate, clear conventions, obvious patterns
- **Speed**: Sub-second hot reload, one command to start, fast iteration
- **Modern Stack**: Latest stable versions, async-first, production-tested
- **Assistant-Friendly**: Works great with Claude, Cursor, and other coding AI

## Quick Links

- **[Quick Start](quick-start.md)** - Get started in 5 minutes
- **[Development Guide](development-guide.md)** - Daily development workflow
- **[Tech Stack](tech-stack.md)** - Technologies and why we chose them
- **[Contributing](contributing.md)** - Help improve Vibetuner

## Project Structure

Generated projects separate framework code from your code:

```
my-app/
├── src/vibetuner/          # Core framework (immutable)
│   ├── frontend/           # FastAPI app, auth, middleware
│   ├── models/             # User, OAuth models
│   └── services/           # Email, storage services
├── src/app/                # Your code (edit freely)
│   ├── frontend/routes/    # Your HTTP routes
│   ├── models/             # Your database models
│   └── services/           # Your business logic
├── templates/              # Jinja2 templates
└── Dockerfile              # Production deployment
```

## Community

- **GitHub**: [alltuner/vibetuner](https://github.com/alltuner/vibetuner)
- **Issues**: [Report bugs or request features](https://github.com/alltuner/vibetuner/issues)
- **PyPI**: [vibetuner](https://pypi.org/project/vibetuner/)
- **npm**: [@alltuner/vibetuner](https://www.npmjs.com/package/@alltuner/vibetuner)

## License

MIT License - Copyright (c) 2025 All Tuner Labs, S.L.

Created by David Poblador i Garcia ([@davidpoblador](https://github.com/davidpoblador) | [davidpoblador.com](https://davidpoblador.com/))
