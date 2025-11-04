# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

This is a **Copier-based project scaffolding template** that generates modern
Python web applications using AllTuner's blessed stack:

- **FastAPI** + **MongoDB** + **HTMX** + **Tailwind CSS/DaisyUI**
- **Docker** containerization with multi-stage builds
- **OAuth + Magic Link authentication**
- **Background task processing** with Redis/Streaq
- **Internationalization** support
- **Dependency management**: Uses `vibetuner` package for Python dependencies
  and `@alltuner/vibetuner` package for JavaScript (build-time) dependencies

## Essential Commands

### Scaffolding Template Management

```bash
# Create new projects
uvx vibetuner scaffold new my-project              # Interactive mode
uvx vibetuner scaffold new my-project --defaults   # Non-interactive with defaults
vibetuner scaffold update                          # Update existing project

# Development commands for the scaffolding itself
just --list                    # List all available commands
just sync                      # Sync all dependencies (Python + JS)
just format                    # Format and check code
just bump-patch                # Version bump the scaffolding template
just pr                        # Create pull request for template changes
just test-scaffold             # Test scaffold command locally
```

### Generated Project Commands (in template/)

When working with generated projects or testing the template:

```bash
# Development
just dev                      # Run dev environment with Docker + watch mode
just local-dev               # Run locally without Docker
just sync                     # Sync all dependencies (uv + bun)

# Building
just build-dev               # Build development Docker image
just test-build-prod         # Test production build
just release                 # Build and push production image (tagged commits only)

# Frontend assets
bun dev                      # Watch mode for CSS/JS (in template/)
bun build-prod              # Production build for CSS/JS

# Localization
just extract-translations    # Extract i18n strings from source
just new-locale LANG         # Create new language file
just update-locale-files     # Update existing translations
just compile-locales         # Compile .po files to .mo
```

## Architecture Overview

### Project Structure

Vibetuner consists of three main components:

1. **Scaffolding System** (root): Copier template configuration
   - `copier.yml`: Template questions and configuration
   - `justfile`: Project management commands
   - `.claude/commands/`: Claude Code slash commands
   - `.github/workflows/`: CI/CD for publishing packages

2. **Python Package** (`vibetuner-py/`): Core framework
   - `src/vibetuner/`: Complete web application framework
   - `src/vibetuner/cli/`: CLI with scaffold and run commands
   - Published to PyPI as `vibetuner`

3. **JavaScript Package** (`vibetuner-js/`): Frontend dependencies
   - Bundles Tailwind CSS, DaisyUI, HTMX, and build tools
   - Published to npm as `@alltuner/vibetuner`

4. **Template** (`template/`): Project template to be copied
   - Generated projects use the published `vibetuner` and `@alltuner/vibetuner` packages
   - Template files use `.j2` extension for Jinja2 processing

### Generated Project Architecture

The template generates a FastAPI application with this structure:

#### Backend

- **`src/vibetuner/`**: Immutable core framework (from vibetuner package)
  - `frontend/`: FastAPI app, routes, auth, middleware
  - `models/`: User, OAuth, core models
  - `services/`: Email (SES), blob storage (S3)
  - `tasks/`: Background job infrastructure
  - `cli/`: CLI framework (scaffold, run commands)
  - Core files: `config.py`, `mongo.py`, `logging.py`

- **`src/app/`**: Your application code
  - `frontend/routes/`: Your HTTP routes
  - `models/`: Your MongoDB models
  - `services/`: Your business logic
  - `tasks/`: Your background jobs
  - `cli/`: Your CLI commands
  - `config.py`: App-specific configuration

#### Frontend

- **HTMX-powered** reactive interfaces without complex JavaScript
- **Tailwind CSS + DaisyUI** for styling
- **Jinja2 templates** in `templates/frontend/`
- **Static assets** compiled to `assets/statics/`

#### Authentication

- **Dual auth system**: OAuth providers + passwordless magic links
- **User model** with OAuth account linking in `models/users.py`
- **Routes** in `frontend/routes/auth.py`

### Key Integration Points

#### Configuration Management

- **`config.py`**: Uses Pydantic settings with environment variable support
- **Environment file**: `.env`
- **Copier variables**: Configured in `copier.yml` for template generation

#### Database Integration

- **MongoDB** with Motor async driver and Beanie ODM
- **Connection setup** in `mongo.py` with automatic model registration
- **Models** extend `BaseModel` with mixins like `TimeStampMixin`

#### Docker Deployment

- **Multi-stage Dockerfile**: Dependencies → app → frontend build → runtime
- **Docker Compose**: Separate configs for dev (`compose.dev.yml.j2`) and prod (`compose.prod.yml.j2`)
- **Health checks** and service orchestration included

## Development Workflow

### Template Development

1. Make changes to files in `template/`
2. Test with `copier copy . /tmp/test-project`
3. Use `just bump-patch` for versioning
4. Create PR with `just pr`

### Generated Project Development

1. **Start development**: `just dev` (Docker) or `just local-dev` (local)
2. **Frontend changes**: `bun dev` watches CSS/JS automatically
3. **Database changes**: Update models in `models/`, migrations handled by application
4. **New features**: Follow FastAPI patterns in `frontend/routes/`

### Testing Generated Projects

- Use `just test-build-prod` to verify production builds work
- Test both authentication flows (OAuth + magic link)
- Verify i18n with multiple languages
- Test background job processing if enabled

## File Patterns

### Template Files (.j2)

- **Jinja2 templates** use Copier variables like `{{ project_slug }}`,
  `{{ author_name }}`
- **Conditional blocks** use `{% if condition %}` for optional features
- **Key files**: `pyproject.toml.j2`, `compose.*.yml.j2`, `start.sh.j2`

### Configuration Files

- **`copier.yml`**: Template configuration and user prompts
- **`pyproject.toml`**: Root project metadata (minimal, no dependencies)
- **`vibetuner-py/pyproject.toml`**: Python package dependencies and metadata
- **`vibetuner-js/package.json`**: JavaScript package dependencies and metadata
- **`template/pyproject.toml.j2`**: Generated project Python dependencies (uses `vibetuner` from PyPI)
- **`template/package.json.j2`**: Generated project JavaScript dependencies (uses `@alltuner/vibetuner` from npm)

### Static Assets

- **CSS**: Tailwind compilation from `config.css` → `assets/statics/css/bundle.css`
- **JS**: esbuild bundling from `config.js` → `assets/statics/js/bundle.js`
- **Versioned URLs**: `/static/v{hash}/` for cache busting

## Common Development Tasks

### Adding New Template Features

1. Update `copier.yml` with new configuration options
2. Add template files in `template/` directory
3. Use Jinja2 conditionals for optional features: `{% if enable_feature %}`
4. Test with different configuration combinations

### Modifying Generated Project Structure

1. Edit files in `template/src/{{ project_slug }}/`
2. Update imports and dependencies in `template/pyproject.toml.j2`
3. Modify Docker build steps if needed
4. Update corresponding justfile commands

### Frontend Development

- **HTMX attributes**: Use `hx-*` attributes for reactive behavior
- **Tailwind classes**: DaisyUI components provide pre-built patterns
- **Template inheritance**: Extend `base/skeleton.html.jinja`
- **Asset pipeline**: Automatic rebuilding with `bun dev`

### Database Schema Changes

- **Model updates**: Modify Beanie models in `models/`
- **Migrations**: Handle programmatically in application startup
- **Indexes**: Define in model `Settings` class
