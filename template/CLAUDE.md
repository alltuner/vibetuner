# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern Python web application built with AllTuner's blessed stack:

- **FastAPI** web framework with async support
- **MongoDB** database with Beanie ODM  
- **HTMX** for reactive frontend interactions
- **Tailwind CSS + DaisyUI** for styling
- **Docker** containerization
- **Redis + Streaq** for background job processing (if enabled)
- **OAuth + Magic Link** authentication

## Essential Commands

### Development

```bash
just dev                     # Run full dev environment with Docker + hot reload
just local-dev              # Run locally without Docker (requires .env.local)
just worker-dev              # Run task worker locally (if job queue enabled)
just sync                    # Sync all dependencies (Python + Node.js)
```

### Frontend Assets

```bash
pnpm dev                     # Watch mode for CSS/JS compilation
pnpm build-prod             # Production build for CSS/JS
```

### Building & Deployment

```bash
just build-dev               # Build development Docker image
just test-build-prod         # Test production build locally
just release                 # Build and push production (tagged commits only)
just deploy-latest HOST      # Deploy to production server (if configured)
```

### Localization

```bash
just extract-translations    # Extract translatable strings from code
just update-locale-files     # Update existing translation files
just compile-locales         # Compile translations for runtime
just new-locale LANG         # Add support for new language
```

### Git Workflow

```bash
just start-branch NAME       # Create new feature branch from main
just commit "MESSAGE"        # Add all changes and commit
just pr                      # Push branch and create GitHub PR
just merge                   # Merge PR with squash
```

### Versioning

```bash
just bump-patch              # Increment patch version (0.1.0 → 0.1.1)
just bump-minor              # Increment minor version (0.1.0 → 0.2.0)  
just bump-major              # Increment major version (0.1.0 → 1.0.0)
```

## Application Architecture

### Backend Structure (`src/[project_slug]/`)

#### Core Application

- **`__main__.py`**: CLI entry point, run with `python -m [project_slug]`
- **`config.py`**: Application configuration using Pydantic Settings
- **`paths.py`**: Static asset and template path management
- **`logging.py`**: Centralized logging configuration
- **`_version.py`**: Dynamic version management from git tags

#### Web Application (`frontend/`)

- **`__init__.py`**: FastAPI app setup, static file mounting, middleware
- **`routes/`**: HTTP route handlers
  - `auth.py`: OAuth and magic link authentication
  - `debug.py`: Development debugging endpoints
- **`templates.py`**: Jinja2 template rendering utilities
- **`deps.py`**: Dependency injection for route handlers
- **`middleware.py`**: Request/response processing middleware

#### Data Layer (`models/`)

- **`user.py`**: User model with OAuth account linking
- **`oauth.py`**: OAuth provider account management
- **`email_verification.py`**: Magic link email authentication tokens
- **`mixins.py`**: Reusable model components (timestamps, etc.)

#### Services (`services/`)

- **`email.py`**: Email sending via AWS SES (if configured)

#### Background Jobs (`tasks/`)

- **`worker.py`**: Streaq task worker setup (if job queue enabled)
- **`context.py`**: Task execution context and dependencies

#### Database Integration

- **`mongo.py`**: MongoDB connection with Motor async driver
- **`mongo_types.py`**: Custom MongoDB type definitions

#### CLI Commands (`cli/`)

- **`__init__.py`**: CLI command registration
- Custom commands can be added here

### Frontend Structure

#### Templates (`templates/`)

- **`frontend/base/skeleton.html.jinja`**: Base HTML layout with HTMX
- **`frontend/defaults/index.html.jinja`**: Homepage template
- **`frontend/login.html.jinja`**: Authentication page
- **`email/`**: Email templates for transactional emails

#### Static Assets (`assets/statics/`)

- **`css/bundle.css`**: Compiled Tailwind CSS (auto-generated)
- **`js/bundle.js`**: Bundled JavaScript with HTMX (auto-generated)
- **`img/`**: Images and logos
- **`favicons/`**: Favicon files

#### Asset Pipeline

- **`config.css`**: Tailwind CSS source file
- **`config.js`**: JavaScript source with HTMX configuration
- **Hot reload**: Changes automatically rebuild and refresh browser

## Development Workflow

### Starting Development

1. **Environment setup**: Copy `.env.example` to `.env.local` and configure
2. **Start services**: `just dev` (Docker) or `just local-dev` (local)
3. **Asset watching**: `pnpm dev` in separate terminal for CSS/JS changes

### Adding New Features

1. **Routes**: Add new endpoints in `src/[project_slug]/frontend/routes/`
2. **Models**: Define data models in `src/[project_slug]/models/`
3. **Templates**: Create Jinja2 templates in `templates/frontend/`
4. **Styles**: Use Tailwind classes, extend in `config.css` if needed

### Authentication System

- **OAuth Flow**: Configured providers in `config.py`, handled in `routes/auth.py`
- **Magic Links**: Passwordless login via email, tokens in `models/email_verification.py`  
- **User Sessions**: FastAPI session middleware with secure cookies
- **Protected Routes**: Use `get_current_user` dependency from `frontend/deps.py`

### Background Jobs  

When job queue is enabled:

- **Define tasks**: Add functions to `src/[project_slug]/tasks/`
- **Queue jobs**: Use Streaq client to enqueue from route handlers
- **Process jobs**: `just worker-dev` runs worker locally
- **Monitor**: Check Redis for job status and results

### Database Operations

- **Models**: Extend `BaseModel` from Beanie ODM
- **Queries**: Use async/await with Beanie query methods
- **Indexes**: Define in model `Settings.indexes`
- **Relationships**: Use `Link` for document references

### Frontend Development

- **HTMX Patterns**: Use `hx-get`, `hx-post`, etc. for dynamic updates
- **Tailwind CSS**: DaisyUI components provide pre-built UI elements
- **Template Inheritance**: Extend `base/skeleton.html.jinja` for consistent layout
- **Forms**: Server-side validation with Pydantic models

## Configuration

### Environment Variables

- **`ENVIRONMENT`**: `development` or `production`
- **`DEBUG`**: Enable debug mode and endpoints
- **`DATABASE_URL`**: MongoDB connection string
- **`REDIS_URL`**: Redis connection for job queue (if enabled)
- **`SECRET_KEY`**: Session encryption key
- **`AWS_*`**: AWS credentials for services (if configured)

### Configuration Files

- **`.env`**: Default environment variables (committed)
- **`.env.local`**: Local overrides (not committed)
- **`config.yaml`**: Optional YAML configuration file
- **`.copier-answers.yml`**: Project metadata and configuration

## Testing

### Running Tests

```bash
# Check pyproject.toml for specific test configuration
# Common patterns:
pytest tests/                    # Run all tests
pytest tests/test_auth.py        # Run specific test file
pytest -k "test_login"           # Run tests matching pattern
```

## Deployment

### Docker Deployment

- **Multi-stage build**: Optimized production image
- **Health checks**: Built-in endpoint monitoring
- **Environment-based**: Different configs for dev/staging/prod

### Production Deployment

- **Process**: `just release` → `just deploy-latest [HOST]`
- **Requirements**: Tagged commit, clean working directory
- **Auto-updates**: Watchtower integration (if enabled)

## Common Tasks

### Adding OAuth Providers

1. Update `config.py` with provider configuration
2. Add provider-specific logic in `frontend/routes/auth.py`
3. Update login template with new provider button

### Adding Background Jobs

When job queue is enabled:

1. Define task function in `src/[project_slug]/tasks/`
2. Import and register in `tasks/__init__.py`
3. Queue from routes using `get_streaq_client()`
4. Handle results and errors appropriately

### Internationalization

1. **Extract**: `just extract-translations` finds translatable strings
2. **Translate**: Edit `.po` files in `locales/[lang]/LC_MESSAGES/`
3. **Compile**: `just compile-locales` builds runtime files
4. **Templates**: Use `{% trans %}` blocks and `_()` functions

### Database Schema Changes

1. **Update models**: Modify Beanie model classes
2. **Migration strategy**: Handle in application startup or separate script
3. **Indexes**: Add to model `Settings.indexes` list
4. **Test thoroughly**: Verify with existing data

## Technology Stack

- **Python**: 3.13+ with modern async support
- **FastAPI**: Latest stable version with async support
- **MongoDB**: Compatible with Motor async driver
- **HTMX**: Version 2.x for modern web interactions  
- **Tailwind CSS**: Version 4.x with DaisyUI components
- **Docker**: Multi-stage builds for production optimization
- **uv**: Fast Python package manager
- **Prototuner**: Base framework providing common utilities

## Project-Specific Notes

This section should be updated with any project-specific information, custom configurations, or special considerations for your application.

# important-instruction-reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
