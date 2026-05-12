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

# Update scaffolding and commit dependency bumps on the current branch (no PR).
# Requires a clean working tree and refuses to run on the default branch.
# Exits 2 (and leaves the conflicted worktree intact) if Copier produces conflict markers.
[group('Dependencies')]
deps-scaffolding:
    #!/usr/bin/env bash
    set -euo pipefail

    DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
        | sed 's@^refs/remotes/origin/@@' || echo main)
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$CURRENT_BRANCH" = "$DEFAULT_BRANCH" ]; then
        echo "Refusing to run on '$DEFAULT_BRANCH'. Switch to a feature branch first."
        exit 1
    fi

    if [ -n "$(git status --porcelain)" ]; then
        echo "Working tree is not clean. Commit or stash changes first."
        git status --short
        exit 1
    fi

    # Phase 1: Update scaffolding (copier bumps manifests like package.json and pyproject.toml)
    just update-scaffolding

    # Check for conflict markers in any file (tracked or new).
    # Pattern is split to avoid matching itself when scanning for unresolved conflicts.
    # `update-scaffolding` above ran `bun install` / `uv sync`, so `.venv/` and
    # `node_modules/` are populated and would otherwise yield false positives
    # (copier's own conflict-marker code, beartype, precompiled binaries).
    # `-I` skips binary files; the directory excludes drop the generated trees.
    CONFLICT_MARKER="<""<""<""<""<""<""<"
    if grep -rIl "$CONFLICT_MARKER" \
        --exclude-dir=.git \
        --exclude-dir=.venv \
        --exclude-dir=node_modules \
        --exclude-dir=.tmp \
        --exclude-dir=dist \
        --exclude-dir=build \
        . >/dev/null 2>&1; then
        echo ""
        echo "Scaffolding update produced conflicts. Resolve them, then run:"
        echo "  git add -A && git commit -m 'chore: update scaffolding'"
        echo "  just update-and-commit-repo-deps"
        exit 2
    fi

    # Commit scaffolding changes
    git add -A
    git diff --cached --quiet || git commit -m "chore: update scaffolding"

    # Phase 2: Update dependencies (runs bun update / uv lock against the bumped manifests,
    # so bun.lock's workspaces mirror resyncs to the committed package.json)
    just update-and-commit-repo-deps

    echo ""
    echo "Done. Review the new commits before pushing."

# Create PR with updated dependencies and scaffolding (uses an isolated worktree).
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

    # Apply scaffolding + deps update inside the worktree. Exit 2 means Copier conflicts;
    # leave the worktree intact so the user can resolve and drive the rest manually.
    set +e
    just deps-scaffolding
    RC=$?
    set -e

    if [ "$RC" -eq 2 ]; then
        trap - ERR INT TERM
        echo ""
        echo "(Worktree left at $WORKTREE_DIR for conflict resolution.)"
        echo "After committing the resolved scaffolding and running the deps update, finish with:"
        echo "  git push -u origin $BRANCH"
        echo "  gh pr create --base main --title 'chore: update dependencies and scaffolding'"
        echo "Then clean up:"
        echo "  cd - && git worktree remove $WORKTREE_DIR"
        exit 0
    elif [ "$RC" -ne 0 ]; then
        exit "$RC"
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

    echo ""
    echo "PR created and ready for review."
    # Clean up worktree since everything is pushed
    cleanup

# Install dependencies from lockfiles
[group('Dependencies')]
install-deps:
    @bun install --frozen-lockfile
    @uv sync --all-extras --all-groups --frozen
