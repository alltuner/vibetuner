#!/usr/bin/env bash
# ABOUTME: Superset workspace setup wrapper.
# ABOUTME: Normalizes Superset env vars and delegates to workspace-setup.sh.
set -euo pipefail

export ROOT_PATH="$SUPERSET_ROOT_PATH"
exec "$(dirname "$0")/workspace-setup.sh"
