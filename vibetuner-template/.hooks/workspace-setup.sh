#!/usr/bin/env bash
# ABOUTME: Shared workspace setup script for all worktree-based tools.
# ABOUTME: Called by tool-specific wrappers that set ROOT_PATH.
set -euo pipefail

if [ -z "${ROOT_PATH:-}" ]; then
    echo "ERROR: ROOT_PATH must be set by the calling wrapper script"
    exit 1
fi

# --- .env symlink ---
for envfile in .env .env.local .envrc; do
    if [ -f "$ROOT_PATH/$envfile" ] && [ ! -e "$envfile" ]; then
        ln -sf "$ROOT_PATH/$envfile" "$envfile"
        echo "✓ Symlinked $envfile"
    fi
done
for srcfile in "$ROOT_PATH"/.env.*.local; do
    [ -f "$srcfile" ] || continue
    envfile="$(basename "$srcfile")"
    [ -e "$envfile" ] && continue
    ln -sf "$srcfile" "$envfile"
    echo "✓ Symlinked $envfile"
done

# --- Dependencies ---
if [ -f "bun.lock" ] || [ -f "package.json" ]; then
    bun install --frozen-lockfile || echo "⚠ bun install failed, continuing anyway"
    echo "✓ Bun dependencies installed"
fi

if [ -f "pyproject.toml" ]; then
    uv sync --all-extras --all-groups --frozen || echo "⚠ uv sync failed, continuing anyway"
    echo "✓ Python dependencies installed"
fi

# --- Pre-commit hooks (prek) ---
if [ -f ".pre-commit-config.yaml" ] && command -v uv >/dev/null 2>&1; then
    if git config --get core.hooksPath >/dev/null 2>&1; then
        git config --local --unset-all core.hooksPath 2>/dev/null || true
    fi
    uv tool run prek install || echo "⚠ prek install failed, continuing anyway"
    echo "✓ Pre-commit hooks installed"
fi
