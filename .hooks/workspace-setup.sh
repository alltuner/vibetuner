#!/usr/bin/env bash
# ABOUTME: Shared workspace setup script for all worktree-based tools.
# ABOUTME: Called by tool-specific wrappers that set ROOT_PATH.
set -euo pipefail

if [ -z "${ROOT_PATH:-}" ]; then
    echo "ERROR: ROOT_PATH must be set by the calling wrapper script"
    exit 1
fi

# --- Python dependencies ---
if [ -f "pyproject.toml" ]; then
    uv sync --frozen
    echo "✓ Python dependencies installed"
fi

# --- JavaScript dependencies ---
for dir in vibetuner-js vibetuner-template; do
    if [ -f "$dir/bun.lock" ] || [ -f "$dir/package.json" ]; then
        (cd "$dir" && bun install --frozen-lockfile)
        echo "✓ Bun dependencies installed in $dir"
    fi
done

# --- Pre-commit hooks (prek) ---
if [ -f ".pre-commit-config.yaml" ] && command -v uv >/dev/null 2>&1; then
    if git config --get core.hooksPath >/dev/null 2>&1; then
        git config --local --unset-all core.hooksPath 2>/dev/null || true
    fi
    uv tool run prek install
    echo "✓ Pre-commit hooks installed"
fi
