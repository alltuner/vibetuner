# Lint GitHub Actions workflow files
[group('Code Quality')]
lint-gh:
    @echo "🔍 Linting GitHub Actions workflows..."
    @uv run actionlint .github/workflows/*.yml
    @echo "✅ GitHub Actions workflows linted successfully"

# Run all linting checks (including GitHub Actions)
[group('Code Quality')]
lint: lint-gh
    @echo "🔍 Running all linting checks..."
    @echo "✅ All linting checks completed"