# Lint markdown files including dot directories
[group('Code quality: linting')]
lint-md:
    @uv run rumdl check . .claude .github

# Lint Python files with ruff
[group('Code quality: linting')]
lint-py:
    @ruff check .

# Lint TOML files with taplo (check only)
[group('Code quality: linting')]
lint-toml:
    @uv run taplo fmt --check

# Lint Jinja files with djlint
[group('Code quality: linting')]
lint-jinja:
    @uv run djlint . --lint

# Lint YAML files with dprint
[group('Code quality: linting')]
lint-yaml:
    @uvx --from dprint-py dprint check --plugins https://plugins.dprint.dev/g-plane/pretty_yaml-v0.5.1.wasm

# Lint PO translation files with lint-po
[group('Code quality: linting')]
lint-po:
    @uvx lint-po locales/*/LC_MESSAGES/*.po

# Type check Python files with ty
[group('Code quality: linting')]
type-check:
    @ty check .

# Run all linting checks
[group('Code quality: linting')]
lint: lint-md lint-py lint-toml lint-jinja lint-po type-check
