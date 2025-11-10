# Lint markdown files including dot directories
[group('linting')]
lint-md:
    @uv run rumdl check . .claude .github

# Lint Python files with ruff
[group('linting')]
lint-py:
    @uv run ruff check .

# Type check Python files with ty (disabled by ty.toml)
[group('linting')]
type-check:
    @uv run ty check .

# Lint TOML files with taplo (check only)
[group('linting')]
lint-toml:
    @uv run taplo fmt --check

# Run all linting checks
[group('linting')]
lint: lint-md lint-py type-check lint-toml