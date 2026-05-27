# Lint GitHub Actions workflow files
[group('Code quality: linting')]
lint-gh:
    @echo "🔍 Linting GitHub Actions workflows..."
    @actionlint .github/workflows/*.yml
    @echo "✅ GitHub Actions workflows linted successfully"

# Type check Python files in vibetuner-py with ty
[group('Code quality: linting')]
type-check-py:
    @cd vibetuner-py && uv run --frozen ty check .

# Run all linting checks (overrides template's recipe to add type-check-py)
[group('Code quality: linting')]
lint: lint-md lint-py lint-toml lint-jinja lint-yaml lint-po type-check type-check-py
