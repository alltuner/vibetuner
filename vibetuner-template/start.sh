#!/bin/sh
set -e

echo "This is the environment:"
env

# Handle special container commands
if [ "$1" = "shell" ]; then
    exec /bin/bash
elif [ "$1" = "sleep" ]; then
    exec sleep 2147483647
fi

# In dev, kick off bun watchers in the background so editing config.css /
# templates / config.js triggers a bundle.css / bundle.js rebuild without
# leaving the container. Skipped in prod or when bun is not in the image.
if [ "$ENVIRONMENT" = "dev" ] && command -v bun > /dev/null 2>&1; then
    bun run dev:css &
    bun run dev:js &
fi

# Pass everything else to vibetuner run commands
if [ -n "$1" ]; then
    # Explicit command provided (e.g., dev, worker, prod)
    exec vibetuner run "$@"
elif [ "$ENVIRONMENT" = "prod" ]; then
    # Production mode when ENVIRONMENT variable is set
    exec vibetuner run prod
else
    # Default to dev mode
    exec vibetuner run dev
fi
