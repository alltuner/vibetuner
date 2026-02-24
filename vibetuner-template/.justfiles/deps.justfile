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
deps-scaffolding-pr:
    #!/usr/bin/env bash
    set -euo pipefail

    BRANCH="chore/deps-scaffolding-$(date +%Y-%m-%d-%H%M)"
    WORKTREE_DIR=$(mktemp -d)

    cleanup() { git worktree remove --force "$WORKTREE_DIR" 2>/dev/null; git branch -D "$BRANCH" 2>/dev/null; }
    trap cleanup ERR

    git fetch origin main
    git worktree add -b "$BRANCH" "$WORKTREE_DIR" origin/main

    cd "$WORKTREE_DIR"

    just update-and-commit-repo-deps

    if [ "$(git rev-list origin/main..HEAD --count)" -eq 0 ]; then
        echo "No dependency changes - continuing with scaffolding update"
        git commit --allow-empty -m "chore: update scaffolding"
    fi

    git push -u origin "$BRANCH"
    DATE=$(date +%Y-%m-%d)
    gh pr create \
        --base main \
        --title "chore: update dependencies and scaffolding ($DATE)" \
        --body "Updates dependencies and scaffolding from upstream vibetuner template."

    # Run scaffolding update (may have conflicts)
    just update-scaffolding

    echo ""
    echo "PR created. Next steps:"
    echo ""
    echo "1. cd $WORKTREE_DIR"
    echo "2. Review scaffolding changes and resolve any conflicts"
    echo "3. Stage and commit your changes:"
    echo "   git add -A && git commit -m 'chore: resolve scaffolding conflicts'"
    echo "4. Push to update the PR:"
    echo "   git push"
    echo "5. Merge the PR when ready"
    echo "6. Remove the worktree:"
    echo "   cd - && git worktree remove $WORKTREE_DIR"
    echo ""

# Install dependencies from lockfiles
[group('Dependencies')]
install-deps:
    @bun install --frozen-lockfile
    @uv sync --all-extras --all-groups --frozen
