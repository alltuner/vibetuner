#!/bin/sh
set -e

# Handle special container commands
if [ "$1" = "shell" ]; then
    exec /bin/bash
elif [ "$1" = "sleep" ]; then
    exec sleep 2147483647
fi

# Pass everything else to vibetuner run commands
if [ -n "$1" ]; then
    # Explicit command provided (e.g., dev, worker, prod)
    exec vibetuner run "$@"
elif [ "$ENVIRONMENT" = "production" ]; then
    # Production mode when ENVIRONMENT variable is set
    exec vibetuner run prod
else
    # Default to dev mode
    exec vibetuner run dev
fi
