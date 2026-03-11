#!/usr/bin/env bash
# ABOUTME: Emdash workspace setup wrapper.
# ABOUTME: Normalizes Emdash env vars and delegates to workspace-setup.sh.
set -euo pipefail

export ROOT_PATH="$EMDASH_ROOT_PATH"
exec "$(dirname "$0")/workspace-setup.sh"
