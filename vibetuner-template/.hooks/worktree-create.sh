#!/usr/bin/env bash
# ABOUTME: Claude Code project-level worktree-create hook.
# ABOUTME: Normalizes Claude env vars and delegates to workspace-setup.sh.
set -euo pipefail

# The global hook doesn't export CLAUDE_PROJECT_DIR to subprocesses,
# so resolve the main worktree path via git.
export ROOT_PATH
ROOT_PATH="$(git rev-parse --path-format=absolute --git-common-dir | sed 's|/\.git$||')"
exec "$(dirname "$0")/workspace-setup.sh"
