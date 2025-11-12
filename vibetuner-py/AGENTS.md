# Vibetuner Python Package Development

This is the core Python framework package for Vibetuner. This guide is for **developers working on the
vibetuner package itself**, not for end users.

## Package Structure

```text
vibetuner-py/
├── src/vibetuner/         # Core framework code
│   ├── cli/              # CLI commands (scaffold, run)
│   ├── frontend/         # FastAPI app, auth, middleware
│   ├── models/           # Core models (User, OAuth, etc.)
│   ├── services/         # Email, blob storage services
│   ├── tasks/            # Background job infrastructure
│   ├── templates/        # Core Jinja2 templates (email, frontend)
│   ├── config.py         # Framework configuration
│   ├── mongo.py          # MongoDB connection setup
│   ├── paths.py          # Path resolution utilities
│   └── templates.py      # Template rendering engine
├── pyproject.toml        # Package metadata and dependencies
└── README.md             # Package documentation
```

## Development Setup

From the repository root:

```bash
# Install in editable mode with dev dependencies
cd vibetuner-py
uv sync

# Test CLI commands
uv run vibetuner --help
uv run vibetuner scaffold new /tmp/test-project --defaults
```

## Key Concepts

### Immutable Framework Code

The code in `src/vibetuner/` is **immutable scaffolding** - it's installed into users' environments but
shouldn't be modified by end users. When you make changes here:

1. They affect ALL projects using this version of vibetuner
2. You must consider backward compatibility
3. Test changes by scaffolding a new project and running it

### Blessed Dependencies

The `dependencies` list in `pyproject.toml` defines the "blessed stack" - the versions of FastAPI,
Beanie, Granian, etc. that we officially support and test against.

### Templates

Core templates in `src/vibetuner/templates/` are packaged with the framework. Users can override them
in their project's `templates/` directory.

## Development Workflow

### Making Framework Changes

1. **Modify code** in `src/vibetuner/`
2. **Format code**: `ruff format .`
3. **Check for issues**: `ruff check --fix .`
4. **Test scaffolding**: Create a test project and verify it works

```bash
# Test that scaffolding still works
uv run vibetuner scaffold new /tmp/test-project --defaults
cd /tmp/test-project
just dev  # Should start without errors
```

### Testing the Scaffold Command

The scaffold command (`vibetuner scaffold`) uses Copier to generate projects from the template at the
repository root. When testing scaffold changes:

```bash
# Test from current branch
uvx git+https://github.com/alltuner/vibetuner@YOUR_BRANCH#subdirectory=vibetuner-py scaffold new /tmp/test
```

### Adding New Dependencies

When adding dependencies to the blessed stack:

1. Add to `dependencies` in `pyproject.toml`
2. Run `uv sync` to update `uv.lock`
3. Document why it's needed in PR description
4. Consider version constraints carefully

### Building the Package

```bash
# Build wheel and sdist
uv build

# Check what's included (AGENTS.md and CLAUDE.md should NOT appear)
unzip -l dist/vibetuner-*.whl

# Test installation from built wheel
uv pip install dist/vibetuner-*.whl
```

## Key Files to Know

### `cli/__init__.py`

The main CLI entry point using Typer. Commands:

- `scaffold new` - Create new project from template
- `scaffold update` - Update existing project
- `run dev` - Run development server
- `run prod` - Run production server

### `config.py`

Framework configuration using Pydantic Settings. This is the **immutable** config that all projects
inherit. User-specific config goes in the scaffolded `src/app/config.py`.

### `frontend/lifespan.py`

FastAPI lifespan management. This sets up:

- MongoDB connection
- Redis connection (if enabled)
- Streaq worker (if background jobs enabled)
- Model registration

Users can extend this via `src/app/frontend/lifespan.py` in their projects.

### `paths.py`

Path resolution utilities that handle both:

- Framework paths (inside installed package)
- Application paths (in user's project)

Critical for template loading and static file serving.

### `templates.py`

Template rendering engine with:

- Automatic context injection (user, request, DEBUG, etc.)
- Template path resolution (user templates override framework templates)
- Jinja2 filters (timeago, format_date, markdown)

## Testing Workflow

1. **Make changes** to framework code
2. **Format and lint**: `ruff format . && ruff check --fix .`
3. **Build package**: `uv build`
4. **Scaffold test project**: `uv run vibetuner scaffold new /tmp/test --defaults`
5. **Test project**: `cd /tmp/test && just dev`
6. **Verify functionality**: Browse to <http://localhost:8000>
7. **Clean up**: `rm -rf /tmp/test`

## Common Pitfalls

### Path Resolution

When adding new features that load files:

- Use `project_paths` from `vibetuner.paths` for user project paths
- Use `package_paths` for framework package paths
- Test that it works both in development and when installed as a package

### Template Changes

When modifying core templates:

- Remember users can override them in their `templates/` directory
- Don't break existing overrides by changing template structure drastically
- Test both with and without user overrides

### Configuration

Don't add application-specific config to `vibetuner/config.py`. Framework config should be:

- Generic (applies to all projects)
- Immutable (users shouldn't need to modify)
- Minimal (only what the framework needs)

Application config goes in the scaffolded `src/app/config.py`.

## Release Process

This package uses Release Please for automated versioning:

1. **PR title format**: `feat:`, `fix:`, `chore:`, etc. (see repo CLAUDE.md)
2. **Merge PR**: Release Please creates/updates a release PR
3. **Merge release PR**: Triggers package publishing to PyPI

## Related Packages

- **vibetuner-template**: The Copier template at repository root
- **@alltuner/vibetuner**: JavaScript package for frontend dependencies
- **vibetuner-docs**: Documentation site

Changes here often need corresponding updates in the template.

## Documentation

End user documentation is in `vibetuner-docs/`:

- `docs/llms-full.txt` - Full documentation for LLMs
- `docs/llms.txt` - Concise documentation with links

Don't duplicate documentation here - this file is for framework developers only.
