#!/bin/sh
set -e

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Starting in production mode..."
    exec castuner webserver main prod
else
    echo "Starting in development mode..."
    exec castuner webserver main dev
fi
