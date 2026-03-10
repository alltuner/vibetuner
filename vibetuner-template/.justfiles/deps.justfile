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
    @git add pyproject.toml uv.lock bun.lock package.json .pre-commit-config.yaml
    @git commit -m "chore: update dependencies" \
        pyproject.toml uv.lock bun.lock package.json .pre-commit-config.yaml \
        || echo "No changes to commit"

# Create PR with updated dependencies and scaffolding
[group('Dependencies')]
deps-scaffolding-pr:
    #!/usr/bin/env bash
    set -euo pipefail

    BRANCH="chore/deps-scaffolding-$(date +%Y-%m-%d-%H%M)"
    WORKTREE_DIR="$(pwd)/.tmp/deps-scaffolding"

    # Clean up leftover worktree from a previous run
    if [ -d "$WORKTREE_DIR" ]; then
        echo "Removing existing worktree..."
        rm -rf "$WORKTREE_DIR/.venv" "$WORKTREE_DIR/node_modules"
        if ! git worktree remove --force "$WORKTREE_DIR" 2>/dev/null; then
            echo "Error: failed to remove worktree at $WORKTREE_DIR"
            echo "Try manually: rm -rf $WORKTREE_DIR && git worktree prune"
            exit 1
        fi
    fi
    mkdir -p .tmp

    cleanup() {
        cd /
        rm -rf "$WORKTREE_DIR/.venv" "$WORKTREE_DIR/node_modules"
        if ! git worktree remove --force "$WORKTREE_DIR" 2>/dev/null; then
            echo "Warning: could not remove worktree at $WORKTREE_DIR"
            echo "Clean up manually: rm -rf $WORKTREE_DIR && git worktree prune"
        fi
        git branch -D "$BRANCH" 2>/dev/null || true
    }
    trap cleanup ERR INT TERM

    git fetch origin main
    git worktree add -b "$BRANCH" "$WORKTREE_DIR" origin/main

    cd "$WORKTREE_DIR"

    # Phase 1: Update dependencies
    just update-and-commit-repo-deps

    # Phase 2: Update scaffolding
    just update-scaffolding

    # Check for conflict markers in any file (tracked or new)
    HAS_CONFLICTS=false
    if grep -rl '<<<<<<<' --exclude-dir=.git . >/dev/null 2>&1; then
        HAS_CONFLICTS=true
    fi

    # Stage and commit scaffolding changes if clean
    if [ "$HAS_CONFLICTS" = false ]; then
        git add -A
        git diff --cached --quiet || git commit -m "chore: update scaffolding"
    fi

    # Bail if nothing changed at all
    if [ "$(git rev-list origin/main..HEAD --count)" -eq 0 ]; then
        echo "Everything is up to date, nothing to do."
        cleanup
        exit 0
    fi

    git push -u origin "$BRANCH"
    DATE=$(date +%Y-%m-%d)
    gh pr create \
        --base main \
        --title "chore: update dependencies and scaffolding ($DATE)" \
        --body "Updates dependencies and scaffolding from upstream vibetuner template."

    if [ "$HAS_CONFLICTS" = true ]; then
        echo ""
        echo "PR created, but scaffolding has conflicts. Next steps:"
        echo ""
        echo "1. cd $WORKTREE_DIR"
        echo "2. Resolve conflicts (look for <<<<<<< markers)"
        echo "3. git add -A && git commit -m 'chore: resolve scaffolding conflicts'"
        echo "4. git push"
        echo "5. Merge the PR, then clean up:"
        echo "   cd - && git worktree remove $WORKTREE_DIR"
    else
        echo ""
        echo "PR created and ready for review."
        # Clean up worktree since everything is pushed
        cleanup
    fi

# Install dependencies from lockfiles
[group('Dependencies')]
install-deps:
    @bun install --frozen-lockfile
    @uv sync --all-extras --all-groups --frozen
