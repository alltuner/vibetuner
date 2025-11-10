# Development Workflow

This guide covers development workflows for working on **Vibetuner itself**, not for using Vibetuner to create projects.
For documentation on using Vibetuner to build applications, see the [Development Guide](development-guide.md).

## Prerequisites

- **Python 3.11+**: For the vibetuner-py package
- **uv**: Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **bun**: JavaScript package manager (`curl -fsSL https://bun.sh/install | bash`)
- **git**: Version control
- **gh CLI** (optional): For creating PRs (`brew install gh` or [cli.github.com](https://cli.github.com/))

## Project Structure

```text
vibetuner/
├── vibetuner-py/          # Python package (published to PyPI)
│   ├── src/vibetuner/     # Core framework code
│   └── pyproject.toml     # Package metadata and dependencies
├── vibetuner-js/          # JavaScript package (published to npm)
│   └── package.json       # Package metadata and dependencies
├── vibetuner-template/       # Copier template (the actual scaffolding)
│   ├── src/vibetuner/     # → Symlink to vibetuner-py/src/vibetuner
│   ├── src/app/           # User application space
│   └── *.j2 files         # Jinja2 templates processed by Copier
├── copier.yml             # Template configuration
├── justfile               # Development commands
├── docs/                  # MkDocs documentation
├── mkdocs.yml             # Documentation configuration
└── .github/workflows/     # CI/CD for publishing
```

## Initial Setup

```bash
# Clone the repository
git clone https://github.com/alltuner/vibetuner
cd vibetuner
# Sync all dependencies
just sync
# This runs:
#   cd vibetuner-py && uv sync
#   cd vibetuner-js && bun install
```

## Common Development Tasks

### Working on the Python Package

```bash
cd vibetuner-py
# Install dependencies
uv sync
# Format code
ruff format .
# Check for issues
ruff check .
# Run the CLI locally
uv run vibetuner --help
uv run vibetuner scaffold new /tmp/test-project
```

### Working on the JavaScript Package

```bash
cd vibetuner-js
# Install dependencies
bun install
# The JS package is just a dependency bundle, no build step
# To test, create a project and run bun dev in it
```

### Working on the Template

```bash
# Test the template generation
just test-scaffold
# This creates /tmp/vibetuner-test with default values
# Or test interactively
copier copy . /tmp/my-test-project
# Test the generated project
cd /tmp/my-test-project
just dev  # Starts Docker development environment
```

For a catalog of template prompts and update flows, see the [Scaffolding Reference](scaffolding.md).

### Testing Scaffold Changes from a Branch

When working on scaffold changes, you can test the CLI directly from a branch without publishing:

```bash
# Test from the current branch (e.g., fix/scaffold-command)
uvx git+https://github.com/alltuner/vibetuner@fix/scaffold-command#subdirectory=vibetuner-py scaffold new --help

# Create a project using the branch
uvx git+https://github.com/alltuner/vibetuner@fix/scaffold-command#subdirectory=vibetuner-py scaffold new /tmp/test-project
```

The CLI also supports a `-b` parameter to specify the branch dynamically:

```bash
# Specify branch with -b parameter
uvx git+https://github.com/alltuner/vibetuner#subdirectory=vibetuner-py scaffold new -b fix/scaffold-command /tmp/test-project
```

This is particularly useful for:

- Testing scaffold changes before merging a PR
- Verifying bug fixes in the scaffold command
- Sharing development versions with collaborators
- CI/CD integration testing

**Note for AI Assistants:** The repository includes a `tmp/` directory at the root with its
contents automatically ignored by git. This directory is specifically for testing scaffold
commands without needing to access external directories like `/tmp`, which can be problematic
for some AI coding assistants:

```bash
# Test scaffolding in the repo's tmp directory
uvx git+https://github.com/alltuner/vibetuner@BRANCH_NAME#subdirectory=vibetuner-py scaffold new ./tmp/test-project
```

### Working on Documentation

```bash
# Serve docs locally with live reload
just docs-serve
# Build docs
just docs-build
# Deploy docs to GitHub Pages
just docs-deploy
```

Visit [localhost:8000](http://localhost:8000) to view the documentation site.

### Adding New Features

1. **Create a feature branch**:

```bash
just start-branch feature-name
```

1. **Make your changes** in the appropriate location:
- Python framework code: `vibetuner-py/src/vibetuner/`
- JavaScript dependencies: `vibetuner-js/package.json`
- Template files: `vibetuner-template/`
- Template configuration: `copier.yml`
- Documentation: `docs/`
2. **Test your changes**:

```bash
just format           # Format and check code
just test-scaffold    # Test scaffolding
just docs-build       # Test docs build
```

1. **Commit your changes**:

```bash
git add .
git commit -m "Add feature X"
```

1. **Push and create PR**:

```bash
git push origin feature-name
just pr               # Creates GitHub PR
```

## Release Workflow

### Version Bumping

```bash
# Patch release (0.0.1 → 0.0.2) - bug fixes, small changes
just bump-patch
# Minor release (0.0.1 → 0.1.0) - new features
just bump-minor
# Major release (0.0.1 → 1.0.0) - breaking changes
just bump-major
```

This will:

1. Update version in `vibetuner-py/pyproject.toml`
2. Create a git commit
3. Create a git tag (e.g., `v0.0.2`)

### Publishing

```bash
# Push tags to trigger GitHub Actions
just push-tags
```

When you push a tag (e.g., `v0.0.2`), GitHub Actions will:

1. Build both Python and JavaScript packages
2. Publish `vibetuner` to PyPI
3. Publish `@alltuner/vibetuner` to npm
4. Deploy documentation to GitHub Pages

The workflow is in `.github/workflows/publish.yml`.

## Testing

### Manual Testing

```bash
# Test scaffold command
just test-scaffold
# Verify the generated project works
cd /tmp/vibetuner-test
just sync     # Install dependencies
just dev      # Start development environment
```

### Testing Changes to the Core Framework

If you modify `vibetuner-py/src/vibetuner/`, you need to test in a generated project:

```bash
# Option 1: Use test-scaffold with local changes
# (The template symlinks to vibetuner-py/src/vibetuner)
just test-scaffold
cd /tmp/vibetuner-test
# Option 2: Create a project and use path dependency
copier copy . /tmp/my-test
cd /tmp/my-test
# Edit pyproject.toml to use: vibetuner = { path = "../vibetuner-py" }
uv sync
just dev
```

## Code Style

### Python

- Use **Ruff** for formatting and linting
- Format before committing: `just format`
- Follow existing patterns in the codebase
- Type hints required
- Async/await for I/O operations

### Templates

- Keep templates simple and readable
- Use descriptive variable names in `copier.yml`

### Documentation

- Use Markdown for all documentation
- Follow existing structure and style
- Link to external resources where appropriate
- Keep examples concise and practical

### Commit Messages

Follow this pattern:

```text
Brief summary of changes (50 chars or less)
More detailed explanation if needed. Wrap at 72 characters.
Include the "why" not just the "what".
🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Troubleshooting

### "Command not found: just"

Install just:

```bash
brew install just
# or
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin
```

### "Command not found: uv"

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "Cannot find module vibetuner"

Make sure dependencies are synced:

```bash
cd vibetuner-py
uv sync
```

### Generated project fails to start

Check:

1. Dependencies installed: `cd /tmp/test-project && uv sync && bun install`
2. MongoDB running: `docker compose up mongodb -d`
3. Redis running (if job queue enabled): `docker compose up redis -d`
4. Environment variables set: Copy `.env.local` to `.env` and configure

### Documentation build fails

Check:

1. MkDocs dependencies installed: `cd vibetuner-py && uv sync --group dev`
2. All referenced files exist
3. No broken internal links

## Project Philosophy

When contributing, keep these principles in mind:

1. **Simplicity**: Prefer simple solutions over clever ones
2. **Speed**: Fast iteration is key - hot reload, minimal config
3. **Modern Stack**: Use latest stable versions, async-first
4. **Assistant-Friendly**: Clear patterns, good documentation, predictable structure

## mise Usage

Generated projects include a `.mise.toml` file that:

- Auto-creates Python virtual environments with `uv`
- Installs tools: `uv`, `bun`, `just`, `gh`

This is **optional** but provides convenience. Projects work fine with just `uv` if you prefer:

```bash
# Without mise
uv sync
uv run vibetuner run dev
# With mise (auto-activates venv)
mise trust
vibetuner run dev
```

The scaffolding project itself doesn't require mise - just `uv` and `bun`.

## Getting Help

- **Issues**: [github.com/alltuner/vibetuner/issues](https://github.com/alltuner/vibetuner/issues)
- **Discussions**: Open an issue for questions
- **Contributing**: See [CONTRIBUTING.md](contributing.md)

## Useful Commands Reference

```bash
# Development
just --list              # Show all available commands
just sync                # Sync all dependencies
just format              # Format and check code
just test-scaffold       # Test scaffolding locally
just clean               # Clean test artifacts
# Documentation
just docs-serve          # Serve docs with live reload
just docs-build          # Build docs
just docs-deploy         # Deploy docs to GitHub Pages
# Releases
just bump-patch          # Bump patch version
just bump-minor          # Bump minor version
just bump-major          # Bump major version
just push-tags           # Push tags to trigger publish
# Git workflow
just start-branch NAME   # Create feature branch
just pr                  # Create GitHub PR
# Testing generated projects
cd /tmp/vibetuner-test
just dev                 # Docker development
just local-dev           # Local development
just sync                # Sync dependencies
just format              # Format code
```
