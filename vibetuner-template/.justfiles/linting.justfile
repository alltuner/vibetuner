# Lint markdown files including dot directories
[group('Code quality: linting')]
lint-md:
    @uv run --frozen rumdl check . .github

# Lint Python files with ruff
[group('Code quality: linting')]
lint-py:
    @uv run --frozen ruff check .

# Lint TOML files with taplo (check only)
[group('Code quality: linting')]
lint-toml:
    @uv run --frozen taplo fmt --check

# Lint Jinja files with djlint
[group('Code quality: linting')]
lint-jinja:
    @uv run --frozen djlint . --lint

# Lint YAML files with dprint
[group('Code quality: linting')]
lint-yaml:
    @uvx --from dprint-py dprint check --plugins https://plugins.dprint.dev/g-plane/pretty_yaml-v0.5.1.wasm

# Lint PO translation files with lint-po
[group('Code quality: linting')]
lint-po:
    @bash -c 'shopt -s nullglob; files=(locales/*/LC_MESSAGES/*.po); if (( ${#files[@]} )); then uvx --from "git+https://github.com/davidpoblador/lint-po@support-gettext-plural-forms" lint-po "${files[@]}"; else echo "No .po files to lint"; fi'

# Type check Python files with ty
[group('Code quality: linting')]
type-check:
    @uv run --frozen ty check .

# Run all linting checks
[group('Code quality: linting')]
lint: lint-md lint-py lint-toml lint-jinja lint-yaml lint-po type-check
