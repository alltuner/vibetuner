#!/bin/sh
set -e

echo "Starting the application..."

if [ "$1" = "shell" ]; then
    echo "Starting shell..."
    exec /bin/bash
elif [ "$1" = "sleep" ]; then
    echo "Container will sleep forever..."
    exec sleep 2147483647
elif [ "$1" = "local-dev" ]; then
    PORT=${PORT:-8000}
    echo "Starting in development mode on port $PORT..."
    DEBUG=1 exec uvicorn core.frontend:app --host 0.0.0.0 --port $PORT --reload --reload-dir src/core --reload-dir templates/frontend --reload-include '*.py' --reload-include '*.html.jinja'
elif [ "$1" = "worker" ]; then
    echo "Starting task worker..."
    exec streaq --web --port 11111 core.tasks.worker.worker
elif [ "$1" = "worker-dev" ]; then
    echo "Starting task worker in development mode..."
    cd src
    DEBUG=1 exec streaq --web --port 11111 --reload --verbose core.tasks.worker.worker
#### Add your custom startup commands below this line
#### End of custom startup commands, do not add anything below
elif [ "$ENVIRONMENT" = "production" ]; then
    echo "Starting in production mode..."
    exec fastapi run src/core/frontend
else
    echo "Starting in development mode..."
    exec fastapi dev --host 0.0.0.0 src/core/frontend
fi
