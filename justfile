# Vibetuner Scaffolding Project Management
# Commands for version management and releases

# List all available commands
default:
    @just --list

# Sync Python dependencies in vibetuner-py
sync-py:
    cd vibetuner-py && uv sync

# Sync JavaScript dependencies in vibetuner-js
sync-js:
    cd vibetuner-js && bun install

# Sync all dependencies
sync: sync-py sync-js

# Format Python code
format-py:
    cd vibetuner-py && ruff format .

# Check Python code
check-py:
    cd vibetuner-py && ruff check .

# Format and check all code
format: format-py check-py

# Bump patch version (0.0.1 -> 0.0.2)
bump-patch:
    #!/usr/bin/env bash
    set -euo pipefail
    cd vibetuner-py
    NEW_VERSION=$(uv run uv-bump patch)
    echo "Bumped to $NEW_VERSION"
    git add pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    git tag "v$NEW_VERSION"
    echo "Created tag v$NEW_VERSION"

# Bump minor version (0.0.1 -> 0.1.0)
bump-minor:
    #!/usr/bin/env bash
    set -euo pipefail
    cd vibetuner-py
    NEW_VERSION=$(uv run uv-bump minor)
    echo "Bumped to $NEW_VERSION"
    git add pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    git tag "v$NEW_VERSION"
    echo "Created tag v$NEW_VERSION"

# Bump major version (0.0.1 -> 1.0.0)
bump-major:
    #!/usr/bin/env bash
    set -euo pipefail
    cd vibetuner-py
    NEW_VERSION=$(uv run uv-bump major)
    echo "Bumped to $NEW_VERSION"
    git add pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    git tag "v$NEW_VERSION"
    echo "Created tag v$NEW_VERSION"

# Push tags to remote
push-tags:
    git push origin --tags

# Create GitHub pull request
pr:
    #!/usr/bin/env bash
    set -euo pipefail
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" = "main" ]; then
        echo "Error: Cannot create PR from main branch"
        exit 1
    fi

    # Get commit messages since branching from main
    COMMITS=$(git log main..HEAD --pretty=format:"- %s")

    # Create PR body
    BODY="## Changes

$COMMITS

🤖 Generated with [Claude Code](https://claude.com/claude-code)"

    gh pr create --fill --body "$BODY" --base main

# Start a new feature branch
start-branch name:
    git checkout -b {{name}}
    echo "Created and switched to branch: {{name}}"

# Test scaffold command locally
test-scaffold:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf /tmp/vibetuner-test
    uv run --directory vibetuner-py vibetuner scaffold new /tmp/vibetuner-test --defaults
    echo "Test project created at /tmp/vibetuner-test"
    echo "To test: cd /tmp/vibetuner-test && just dev"

# Clean test artifacts
clean:
    rm -rf /tmp/vibetuner-test
    rm -rf vibetuner-py/dist
    rm -rf vibetuner-js/*.tgz
