import 'deps.justfile'

# Runs the dev environment with watch mode and cleans up orphans
[group('Local Development')]
dev: install-deps
    ENVIRONMENT=development \
    COMPOSE_BAKE=true \
    PYTHON_VERSION={{ PYTHON_VERSION }} \
    COMPOSE_PROJECT_NAME={{ PROJECT_SLUG }} \
    docker compose -f compose.dev.yml up --watch --remove-orphans

# Runs the dev environment locally without Docker
[group('Local Development')]
local-dev PORT="8000": install-deps
    @vibetuner run dev --port {{ PORT }}

# Runs the task worker locally without Docker
[group('Local Development')]
worker-dev: install-deps
    @vibetuner run dev worker