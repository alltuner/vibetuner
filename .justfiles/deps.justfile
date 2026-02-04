
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
    @cd vibetuner-template && bun update

# Update root scaffolding deps
[group('Dependencies')]
update-root:
    @uvx uv-bump && uv lock --upgrade && uv sync --all-extras

# Update all package dependencies
[group('Dependencies')]
update-all: update-js update-py update-template update-root

# Update all dependencies and commit changes
[group('Dependencies')]
update-and-commit: update-all update-precommit
    @git add pyproject.toml uv.lock \
        vibetuner-js/package.json vibetuner-js/bun.lock \
        vibetuner-py/pyproject.toml vibetuner-py/uv.lock \
        vibetuner-template/package.json

    @git commit -m "chore: update dependencies" \
        pyproject.toml uv.lock \
        vibetuner-js/package.json vibetuner-js/bun.lock \
        vibetuner-py/pyproject.toml vibetuner-py/uv.lock \
        vibetuner-template/package.json \
        || echo "No changes to commit"

# Update pre-commit hooks and commit changes
[group('Dependencies')]
update-precommit:
    @uv run prek auto-update
    @git add vibetuner-template/.pre-commit-config.yaml
    @git commit -m "chore: update pre-commit hooks" \
        vibetuner-template/.pre-commit-config.yaml \
        || echo "No pre-commit changes to commit"

# Full dependency update cycle: update deps, pre-commit, create PR, merge, return to main
[group('Dependencies')]
deps-pr:
    #!/usr/bin/env bash
    set -euo pipefail

    # Generate timestamped branch name
    DATE_STAMP=$(date +%Y-%m-%d)
    BRANCH="chore/update-deps-${DATE_STAMP}-$(date +%H%M)"

    # Ensure we're on main and up to date
    git checkout main
    git pull origin main

    # Create feature branch
    git checkout -b "$BRANCH"

    # Update dependencies and pre-commit hooks
    just update-and-commit

    # Check if we have any commits beyond main
    if [ "$(git rev-list main..HEAD --count)" -eq 0 ]; then
        echo "✅ All dependencies already up to date"
        git checkout main
        git branch -D "$BRANCH"
        exit 0
    fi

    # Push and create PR
    git push -u origin "$BRANCH"
    gh pr create --title "chore: update deps ${DATE_STAMP}" --body "" --base main

    # Merge the PR (squash) with conventional commit title
    gh pr merge --squash --delete-branch --subject "chore: update deps ${DATE_STAMP}"

    # Return to main
    git checkout main
    git pull origin main
    echo "✅ Dependencies updated and merged"
