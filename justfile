set allow-duplicate-recipes := true

import 'template/base.justfile'

# Default: update dependencies
default: update-deps

# Create a GitHub release from the latest tag
[group('gitflow')]
gh-release:
    #!/usr/bin/env bash
    LATEST_TAG=$(git describe --tags --abbrev=0 --match "v*" 2>/dev/null)
    if [ -z "$LATEST_TAG" ]; then
        echo "❌ No version tags found."
        exit 1
    fi

    echo "Creating GitHub release for tag: $LATEST_TAG"

    # Generate release notes from commits since previous tag
    PREV_TAG=$(git describe --tags --abbrev=0 "$LATEST_TAG^" 2>/dev/null || echo "")
    if [ -z "$PREV_TAG" ]; then
        NOTES=$(git log --pretty=format:'- %s' "$LATEST_TAG")
    else
        NOTES=$(git log --pretty=format:'- %s' "$PREV_TAG..$LATEST_TAG")
    fi

    gh release create "$LATEST_TAG" \
        --title "$LATEST_TAG" \
        --notes "$NOTES"

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
