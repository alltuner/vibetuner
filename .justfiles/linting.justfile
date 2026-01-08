# Lint GitHub Actions workflow files
[group('Code quality: linting')]
lint-gh:
    @echo "🔍 Linting GitHub Actions workflows..."
    @actionlint .github/workflows/*.yml
    @echo "✅ GitHub Actions workflows linted successfully"
