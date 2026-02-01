# ABOUTME: Git worktree management commands
# ABOUTME: Enables feature branch development in isolated worktrees

# Create a new feature worktree
[group('Features')]
feature-new NAME:
    #!/usr/bin/env bash
    set -euo pipefail
    BRANCH_NAME="{{NAME}}"
    SAFE_NAME=$(echo "$BRANCH_NAME" | tr '/' '-')
    REPO_ROOT=$(git rev-parse --show-toplevel)
    REPO_NAME=$(basename "$REPO_ROOT")
    WORKTREE_BASE="$(dirname "$REPO_ROOT")/${REPO_NAME}.wt"
    WORKTREE_DIR="${WORKTREE_BASE}/${SAFE_NAME}"
    mkdir -p "$WORKTREE_BASE"
    git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" main
    if [[ -f .env ]]; then
        ln -sf "${REPO_ROOT}/.env" "$WORKTREE_DIR/.env"
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
feature-done NAME="":
    #!/usr/bin/env bash
    set -euo pipefail

    INPUT="{{NAME}}"
    BRANCH_NAME=""
    WORKTREE_DIR=""
    RAN_FROM_WORKTREE=false

    if [[ -z "$INPUT" ]]; then
        # No argument: detect current worktree
        CURRENT_DIR=$(pwd)
        if [[ "$CURRENT_DIR" != *".wt/"* ]]; then
            echo "Error: Not in a worktree directory. Provide a branch name or path."
            exit 1
        fi
        BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
        WORKTREE_DIR=$(git rev-parse --show-toplevel)
        RAN_FROM_WORKTREE=true
    elif [[ -d "$INPUT" ]]; then
        # Input is a directory path
        WORKTREE_DIR=$(cd "$INPUT" && git rev-parse --show-toplevel)
        BRANCH_NAME=$(cd "$INPUT" && git rev-parse --abbrev-ref HEAD)
    else
        # Input is a branch name
        BRANCH_NAME="$INPUT"
        SAFE_NAME=$(echo "$BRANCH_NAME" | tr '/' '-')
        REPO_ROOT=$(git rev-parse --show-toplevel)
        REPO_NAME=$(basename "$REPO_ROOT")
        WORKTREE_DIR="$(dirname "$REPO_ROOT")/${REPO_NAME}.wt/${SAFE_NAME}"
    fi

    if [[ ! -d "$WORKTREE_DIR" ]]; then
        echo "Error: Worktree not found at $WORKTREE_DIR"
        exit 1
    fi

    # Get main worktree path before removing
    MAIN_WORKTREE=$(git worktree list --porcelain | grep -m1 '^worktree ' | cut -d' ' -f2-)

    git worktree remove "$WORKTREE_DIR"
    cd "$MAIN_WORKTREE"
    git branch -d "$BRANCH_NAME"
    echo "Removed worktree and branch: $BRANCH_NAME"

    if [[ "$RAN_FROM_WORKTREE" == true ]]; then
        echo ""
        echo "You are now in a deleted directory. Run:"
        echo "  cd $MAIN_WORKTREE"
    fi

# Force remove a feature worktree and delete branch (even if unmerged)
[group('Features')]
feature-drop NAME="":
    #!/usr/bin/env bash
    set -euo pipefail

    INPUT="{{NAME}}"
    BRANCH_NAME=""
    WORKTREE_DIR=""
    RAN_FROM_WORKTREE=false

    if [[ -z "$INPUT" ]]; then
        # No argument: detect current worktree
        CURRENT_DIR=$(pwd)
        if [[ "$CURRENT_DIR" != *".wt/"* ]]; then
            echo "Error: Not in a worktree directory. Provide a branch name or path."
            exit 1
        fi
        BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
        WORKTREE_DIR=$(git rev-parse --show-toplevel)
        RAN_FROM_WORKTREE=true
    elif [[ -d "$INPUT" ]]; then
        # Input is a directory path
        WORKTREE_DIR=$(cd "$INPUT" && git rev-parse --show-toplevel)
        BRANCH_NAME=$(cd "$INPUT" && git rev-parse --abbrev-ref HEAD)
    else
        # Input is a branch name
        BRANCH_NAME="$INPUT"
        SAFE_NAME=$(echo "$BRANCH_NAME" | tr '/' '-')
        REPO_ROOT=$(git rev-parse --show-toplevel)
        REPO_NAME=$(basename "$REPO_ROOT")
        WORKTREE_DIR="$(dirname "$REPO_ROOT")/${REPO_NAME}.wt/${SAFE_NAME}"
    fi

    if [[ ! -d "$WORKTREE_DIR" ]]; then
        echo "Error: Worktree not found at $WORKTREE_DIR"
        exit 1
    fi

    # Get main worktree path before removing
    MAIN_WORKTREE=$(git worktree list --porcelain | grep -m1 '^worktree ' | cut -d' ' -f2-)

    git worktree remove --force "$WORKTREE_DIR"
    cd "$MAIN_WORKTREE"
    git branch -D "$BRANCH_NAME"
    echo "Force removed worktree and branch: $BRANCH_NAME"

    if [[ "$RAN_FROM_WORKTREE" == true ]]; then
        echo ""
        echo "You are now in a deleted directory. Run:"
        echo "  cd $MAIN_WORKTREE"
    fi

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
            if [[ "$path" == *".wt/"* ]]; then
                read -r head_line
                read -r branch_line
                branch="${branch_line#branch refs/heads/}"
                echo "  $branch"
                echo "    -> $path"
                echo ""
            fi
        fi
    done

# Rebase current worktree branch on origin/main
[group('Features')]
feature-rebase:
    git fetch origin main
    git rebase origin/main
