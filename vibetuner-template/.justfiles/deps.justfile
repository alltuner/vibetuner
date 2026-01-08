# Update root scaffolding deps
[group('Dependencies')]
update-repo-deps:
    @uvx uv-bump
    @uv lock --upgrade
    @uv sync --all-extras
    @bun update

# Update all dependencies and commit changes
[group('Dependencies')]
update-and-commit-repo-deps: update-repo-deps
    @git add pyproject.toml uv.lock bun.lock package.json
    @git commit -m "chore: update dependencies" \
        pyproject.toml uv.lock bun.lock package.json \
        || echo "No changes to commit"

# Create PR with updated dependencies and scaffolding
[group('Dependencies')]
deps-scaffolding-pr: _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    # Ensure we're on main
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo "❌ Must be on main branch (currently on $CURRENT_BRANCH)"
        exit 1
    fi

    # Ensure main is up to date
    git pull origin main

    # Generate timestamped branch name
    BRANCH="chore/deps-scaffolding-$(date +%Y-%m-%d-%H%M)"

    # Create feature branch
    git checkout -b "$BRANCH"

    # Update dependencies and commit
    just update-and-commit-repo-deps

    # Check if deps commit was created
    if [ "$(git rev-list main..HEAD --count)" -eq 0 ]; then
        echo "ℹ️  No dependency changes - continuing with scaffolding update"
        # Create empty commit so we can push and create PR
        git commit --allow-empty -m "chore: update scaffolding"
    fi

    # Push and create PR
    git push -u origin "$BRANCH"
    DATE=$(date +%Y-%m-%d)
    gh pr create \
        --base main \
        --title "chore: update dependencies and scaffolding ($DATE)" \
        --body "Updates dependencies and scaffolding from upstream vibetuner template."

    # Run scaffolding update (may have conflicts)
    just update-scaffolding

    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📋 PR created. Next steps:"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "1. Review scaffolding changes and resolve any conflicts"
    echo "2. Stage and commit your changes:"
    echo "   git add -A && git commit -m 'chore: resolve scaffolding conflicts'"
    echo "3. Push to update the PR:"
    echo "   git push"
    echo "4. Merge the PR when ready"
    echo ""

# Install dependencies from lockfiles
[group('Dependencies')]
install-deps:
    @bun install
    @uv sync --all-extras