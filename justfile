# Vibetuner Scaffolding Project Management
# Commands for version management and releases

import 'copier-template/base.justfile'

# List all available commands
default:
    @just --list

# Sync Python dependencies in vibetuner-py
[group('Dependencies')]
sync-py:
    cd vibetuner-py && uv sync

# Sync JavaScript dependencies in vibetuner-js
[group('Dependencies')]
sync-js:
    cd vibetuner-js && bun install

# Sync all dependencies (scaffolding packages)
[group('Dependencies')]
sync: sync-py sync-js

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

# Test scaffold command locally
[group('Scaffolding')]
test-scaffold:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf /tmp/vibetuner-test
    uv run --directory vibetuner-py vibetuner scaffold new /tmp/vibetuner-test --defaults
    echo "Test project created at /tmp/vibetuner-test"
    echo "To test: cd /tmp/vibetuner-test && just dev"

# Clean test artifacts
[group('Scaffolding')]
clean:
    rm -rf /tmp/vibetuner-test
    rm -rf vibetuner-py/dist
    rm -rf vibetuner-js/*.tgz
    rm -rf _site

# Serve documentation locally with live reload
[group('Documentation')]
docs-serve:
    uv sync --only-group docs
    uv run mkdocs serve

# Build documentation
[group('Documentation')]
docs-build:
    uv sync --only-group docs
    uv run mkdocs build --site-dir _site
