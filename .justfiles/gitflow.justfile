# ABOUTME: Git workflow automation commands for the vibetuner monorepo.
# ABOUTME: Provides automated dependency update PR workflow.

# Automated dependency update PR workflow: updates deps, pre-commit, creates PR, merges, returns to main
[group('gitflow')]
deps-pr:
    #!/usr/bin/env bash
    set -euo pipefail

    # Generate timestamped branch name
    BRANCH="chore/update-deps-$(date +%Y-%m-%d-%H%M)"

    # Ensure we're on main and up to date
    git checkout main
    git pull origin main

    # Create feature branch
    git checkout -b "$BRANCH"

    # Update dependencies (reuse existing recipe)
    just update-and-commit

    # Update pre-commit hooks
    uv run prek auto-update
    git add vibetuner-template/.pre-commit-config.yaml
    git commit -m "chore: update pre-commit hooks" \
        vibetuner-template/.pre-commit-config.yaml \
        || echo "No pre-commit changes to commit"

    # Check if we have any commits beyond main
    if [ "$(git rev-list main..HEAD --count)" -eq 0 ]; then
        echo "✅ All dependencies already up to date"
        git checkout main
        git branch -D "$BRANCH"
        exit 0
    fi

    # Push and create PR
    git push -u origin "$BRANCH"
    gh pr create --fill --base main

    # Merge the PR (squash)
    gh pr merge --squash --delete-branch

    # Return to main
    git checkout main
    git pull origin main
    echo "✅ Dependencies updated and merged"
