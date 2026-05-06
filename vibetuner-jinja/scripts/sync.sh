#!/usr/bin/env bash
# ABOUTME: Syncs vibetuner core jinja templates from vibetuner-py into this package.
# ABOUTME: Idempotent. No-op when source is unavailable (e.g. npm-registry install).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$PKG_ROOT/../vibetuner-py/src/vibetuner/templates/frontend"
DST="$PKG_ROOT/templates"
MARKER="$DST/.synced-from-py"

# Source unavailable: we're being installed from a published tarball that
# already contains templates/. Nothing to do.
if [ ! -d "$SRC" ]; then
    exit 0
fi

# Skip if destination is up-to-date with source. The marker file lets us
# detect whether anything in the source tree has been modified since the
# last sync without comparing every file.
if [ -f "$MARKER" ] && [ -z "$(find "$SRC" -type f -newer "$MARKER" -print -quit 2>/dev/null)" ]; then
    exit 0
fi

rm -rf "$DST"
cp -R "$SRC" "$DST"
find "$DST" \( -name AGENTS.md -o -name CLAUDE.md \) -delete
touch "$MARKER"
echo "✓ vibetuner-jinja/templates synced from vibetuner-py"
