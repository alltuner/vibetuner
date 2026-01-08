# ABOUTME: Git worktree management commands
# ABOUTME: Enables feature branch development in isolated worktrees

# Helper to compute worktree directory from branch name
_worktree-dir NAME:
    @echo "worktrees/$(echo -n '{{NAME}}' | sha256sum | cut -c1-8)"

# Create a new feature worktree
[group('Features')]
feature-new NAME:
    #!/usr/bin/env bash
    set -euo pipefail
    BRANCH_NAME="{{NAME}}"
    HASH=$(echo -n "$BRANCH_NAME" | sha256sum | cut -c1-8)
    WORKTREE_DIR="worktrees/$HASH"
    mkdir -p worktrees
    git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" main
    if [[ -f .env ]]; then
        ln -sf "$(pwd)/.env" "$WORKTREE_DIR/.env"
    fi
    command -v mise &> /dev/null && (cd "$WORKTREE_DIR" && mise trust) || true
    echo ""
    echo "Worktree created at: $WORKTREE_DIR"
    echo "Branch: $BRANCH_NAME"
    echo ""
    echo "To start working:"
    echo "  cd $WORKTREE_DIR"

# Remove a feature worktree and delete branch (fails if unmerged)
[group('Features')]
feature-done NAME:
    #!/usr/bin/env bash
    set -euo pipefail
    BRANCH_NAME="{{NAME}}"
    HASH=$(echo -n "$BRANCH_NAME" | sha256sum | cut -c1-8)
    WORKTREE_DIR="worktrees/$HASH"
    if [[ ! -d "$WORKTREE_DIR" ]]; then
        echo "Error: Worktree not found at $WORKTREE_DIR"
        exit 1
    fi
    git worktree remove "$WORKTREE_DIR"
    git branch -d "$BRANCH_NAME"
    echo "Removed worktree and branch: $BRANCH_NAME"

# Force remove a feature worktree and delete branch (even if unmerged)
[group('Features')]
feature-drop NAME:
    #!/usr/bin/env bash
    set -euo pipefail
    BRANCH_NAME="{{NAME}}"
    HASH=$(echo -n "$BRANCH_NAME" | sha256sum | cut -c1-8)
    WORKTREE_DIR="worktrees/$HASH"
    if [[ ! -d "$WORKTREE_DIR" ]]; then
        echo "Error: Worktree not found at $WORKTREE_DIR"
        exit 1
    fi
    git worktree remove --force "$WORKTREE_DIR"
    git branch -D "$BRANCH_NAME"
    echo "Force removed worktree and branch: $BRANCH_NAME"

# List all feature worktrees
[group('Features')]
feature-list:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Feature worktrees:"
    echo ""
    git worktree list --porcelain | while read -r line; do
        if [[ "$line" == worktree* ]]; then
            path="${line#worktree }"
            if [[ "$path" == *"/worktrees/"* ]]; then
                read -r head_line
                read -r branch_line
                branch="${branch_line#branch refs/heads/}"
                echo "  $branch"
                echo "    → $path"
                echo ""
            fi
        fi
    done

# Rebase current worktree branch on origin/main
[group('Features')]
feature-rebase:
    git fetch origin main
    git rebase origin/main
