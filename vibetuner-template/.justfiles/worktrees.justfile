# ABOUTME: Git worktree management commands
# ABOUTME: Enables feature branch development in isolated worktrees

# Start a new feature in a worktree
feature NAME:
    #!/usr/bin/env bash
    set -euo pipefail

    WORKTREE_DIR="worktrees/{{NAME}}"
    BRANCH_NAME="{{NAME}}"

    # Create worktrees directory if needed
    mkdir -p worktrees

    # Create worktree from main
    git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" main

    # Symlink .env if it exists
    if [[ -f .env ]]; then
        ln -sf "$(pwd)/.env" "$WORKTREE_DIR/.env"
    fi

    # Trust mise configuration in the worktree
    (cd "$WORKTREE_DIR" && mise trust)

    echo ""
    echo "Worktree created at: $WORKTREE_DIR"
    echo "Branch: $BRANCH_NAME"
    echo ""
    echo "To start working:"
    echo "  cd $WORKTREE_DIR"
