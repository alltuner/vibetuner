#!/usr/bin/env bash
# ABOUTME: Conductor workspace setup wrapper.
# ABOUTME: Normalizes Conductor env vars and delegates to workspace-setup.sh.
set -euo pipefail

export ROOT_PATH="$CONDUCTOR_ROOT_PATH"
exec "$(dirname "$0")/workspace-setup.sh"
