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
- **Dependency management**: Uses `prototuner` package for both Python
  (runtime) and JavaScript (build-time) dependencies

## Essential Commands

### Scaffolding Template Management

```bash
# Main development commands for the scaffolding itself
just --list                    # List all available commands
just bump-patch               # Version bump the scaffolding template
just pr                       # Create pull request for template changes
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

### Template Structure

- **Root**: Copier configuration (`copier.yml`) and template management
- **template/**: The actual project template that gets generated
- **template/src/{{ project_slug }}/**: Main Python application code

### Generated Project Architecture

The template generates a FastAPI application with this structure:

#### Backend (`src/{{ project_slug }}/`)

- **`frontend/`**: FastAPI app with routes, templates, middleware
- **`models/`**: Beanie ODM models for MongoDB
- **`services/`**: Business logic (email, external APIs)
- **`tasks/`**: Background job processing with Streaq
- **`cli/`**: Typer-based command line interface
- **Core files**: `config.py` (Pydantic settings), `paths.py`, `logging.py`

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
- **`pyproject.toml`**: Scaffolding dependencies (minimal)
- **`template/pyproject.toml.j2`**: Generated project Python dependencies (uses `prototuner` from GitHub)
- **`template/package.json`**: Generated project JavaScript dependencies (uses `prototuner` from GitHub)

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
