# Lint markdown files including dot directories
[group('linting')]
lint-md:
    @uv run rumdl check . .claude .github

# Lint Python files with ruff
[group('linting')]
lint-py:
    @uv run ruff check .


# Lint TOML files with taplo (check only)
[group('linting')]
lint-toml:
    @uv run taplo fmt --check

# Lint Jinja files with djlint
[group('linting')]
lint-jinja:
    @uv run djlint . --lint

# Lint YAML files with dprint
[group('linting')]
lint-yaml:
    @uvx --from dprint-py dprint check --plugins https://plugins.dprint.dev/g-plane/pretty_yaml-v0.5.1.wasm

# Type check Python files with ty
[group('linting')]
type-check:
    @uv run ty check .

# Run all linting checks
[group('linting')]
lint: lint-md lint-py lint-toml lint-jinja type-check
