# Quick Start

Get started with Vibetuner in 5 minutes.

## Prerequisites

- **Python 3.11+**: [python.org/downloads](https://www.python.org/downloads/)
- **Docker**: [docker.com/get-started](https://www.docker.com/get-started/) (for containerized development)

That's it! Vibetuner handles the rest.

## Create Your First Project

### Using uvx (Recommended)

No installation needed:

```bash
uvx vibetuner scaffold new my-app
```

### Install Globally

```bash
uv tool install vibetuner
vibetuner scaffold new my-app
```

### Interactive Setup

The scaffold command will ask you:

- **Project name**: `my-app`
- **Company name**: Your company/organization
- **Author details**: Name and email
- **Features**: OAuth providers, background jobs, etc.

### Skip Prompts

Use defaults for everything:

```bash
uvx vibetuner scaffold new my-app --defaults
```

## Start Development

```bash
cd my-app
just dev
```

This starts:

- MongoDB database
- Redis (if background jobs enabled)
- FastAPI application with hot reload
- Frontend asset compilation

Visit `http://localhost:8000` - your app is running!

## Project Structure

```text
my-app/
├── src/vibetuner/          # Core framework (don't edit)
│   ├── frontend/           # FastAPI app, auth, middleware
│   ├── models/             # User, OAuth models
│   └── services/           # Email, storage services
├── src/app/                # Your code (edit freely)
│   ├── frontend/routes/    # Your HTTP routes
│   ├── models/             # Your database models
│   └── services/           # Your business logic
├── templates/              # Jinja2 templates
├── assets/                 # Static files
└── Dockerfile              # Production deployment
```

## Next Steps

- **Add routes**: Create files in `src/app/frontend/routes/`
- **Define models**: Create Beanie models in `src/app/models/`
- **Customize templates**: Edit files in `templates/`
- **Configure environment**: Copy `.env.local` to `.env` and customize

## Common Commands

```bash
just dev              # Docker development with hot reload
just local-dev        # Local development (no Docker)
just sync             # Sync dependencies
just format           # Format code
just build-prod       # Test production build
```

## Development Modes

### Docker Development (Recommended)

```bash
just dev
```

Everything runs in containers with hot reload. Changes to code, templates, and assets automatically reload.

### Local Development

```bash
# Terminal 1: Frontend assets
bun dev
# Terminal 2: Backend server
just local-dev
```

Useful when you want more control or Docker is slow on your system.

## What's Next?

- [Development Guide](development-guide.md) - Daily development workflow
- [Authentication](authentication.md) - Set up OAuth and magic links
- [Deployment](deployment.md) - Deploy to production
