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

    # Phase 1: Update scaffolding (copier bumps manifests like package.json and pyproject.toml)
    just update-scaffolding

    # Check for conflict markers in any file (tracked or new)
    # Pattern is split to avoid matching itself when scanning for unresolved conflicts
    CONFLICT_MARKER="<""<""<""<""<""<""<"
    if grep -rl "$CONFLICT_MARKER" --exclude-dir=.git . >/dev/null 2>&1; then
        # Leave the worktree and branch in place so the user can resolve conflicts
        # and drive the remaining steps manually. Running the dependency update now
        # would fail against manifests containing conflict markers.
        trap - ERR INT TERM
        echo ""
        echo "Scaffolding update produced conflicts. Next steps:"
        echo ""
        echo "1. cd $WORKTREE_DIR"
        echo "2. Resolve conflicts (look for $CONFLICT_MARKER markers)"
        echo "3. git add -A && git commit -m 'chore: update scaffolding'"
        echo "4. just update-and-commit-repo-deps"
        echo "5. git push -u origin $BRANCH"
        echo "6. gh pr create --base main --title 'chore: update dependencies and scaffolding'"
        echo "7. Merge the PR, then clean up:"
        echo "   cd - && git worktree remove $WORKTREE_DIR"
        exit 0
    fi

    # Commit scaffolding changes
    git add -A
    git diff --cached --quiet || git commit -m "chore: update scaffolding"

    # Phase 2: Update dependencies (runs bun update / uv lock against the bumped manifests,
    # so bun.lock's workspaces mirror resyncs to the committed package.json)
    just update-and-commit-repo-deps

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

    echo ""
    echo "PR created and ready for review."
    # Clean up worktree since everything is pushed
    cleanup

# Install dependencies from lockfiles
[group('Dependencies')]
install-deps:
    @bun install --frozen-lockfile
    @uv sync --all-extras --all-groups --frozen
