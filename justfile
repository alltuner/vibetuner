# Vibetuner Scaffolding Project Management
# Commands for version management and releases

import 'vibetuner-template/base.justfile'

# List all available commands
default:
    @just --list

# Update JavaScript dependencies in vibetuner-js
[group('Dependencies')]
update-js:
    @cd vibetuner-js && bun update

# Update Python dependencies in vibetuner-py
[group('Dependencies')]
update-py:
    @cd vibetuner-py && uvx uv-bump && uv lock --upgrade && uv sync --all-extras

# Update dependencies in vibetuner-template
[group('Dependencies')]
update-template:
    @cd vibetuner-template && uvx uv-bump && uv lock --upgrade && uv sync --all-extras

# Update all package dependencies
[group('Dependencies')]
update-all: update-js update-py update-template

# Update all dependencies and commit changes
[group('Dependencies')]
update-and-commit: update-all
    @git add vibetuner-js/package.json vibetuner-js/bun.lock vibetuner-py/pyproject.toml vibetuner-py/uv.lock vibetuner-template/pyproject.toml vibetuner-template/uv.lock
    @git commit -m "chore: update dependencies"

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
    cd vibetuner-docs && uvx --with mkdocs-material mkdocs serve

# Build documentation
[group('Documentation')]
docs-build:
    cd vibetuner-docs && uvx --with mkdocs-material mkdocs build --site-dir ../_site
