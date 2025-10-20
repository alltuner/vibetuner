set allow-duplicate-recipes := true

import 'template/base.justfile'

# Default: update dependencies
default: update-deps

# Lint markdown files including dot directories
[group('linting')]
lint-md:
    uv run rumdl check . .claude .github template template/.*

# Run all linting checks (scaffolding-specific: no type-check, no jinja)
[group('linting')]
lint: lint-md lint-py lint-toml

# Format all code (scaffolding-specific: no jinja)
[group('formatting')]
format: format-py format-toml
