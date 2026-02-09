import 'deps.justfile'

# Runs the dev environment with watch mode and cleans up orphans
[group('Local Development')]
dev:
    ENVIRONMENT=development \
    COMPOSE_BAKE=true \
    PYTHON_VERSION={{ PYTHON_VERSION }} \
    COMPOSE_PROJECT_NAME={{ PROJECT_SLUG }} \
    docker compose -f compose.dev.yml up --watch --remove-orphans

# Runs the dev environment locally without Docker
[group('Local Development')]
local-dev PORT="8000":
    @DEBUG=true uv run vibetuner run dev --port {{ PORT }}

# Runs local dev with auto-assigned port (deterministic per project path)
[group('Local Development')]
local-dev-auto:
    @DEBUG=true uv run vibetuner run dev --auto-port

# Runs the task worker locally without Docker
[group('Local Development')]
worker-dev:
    @DEBUG=true uv run vibetuner run dev worker

_ensure-deps:
    @[ -d node_modules ] || bun install
    @[ -d .venv ] || uv sync --all-extras

# Runs local dev server and assets in parallel (auto-port)
[group('Local Development')]
local-all: _ensure-deps
    bunx concurrently --kill-others \
        --names "web,assets" \
        --prefix-colors "blue,green" \
        "just local-dev-auto" \
        "bun dev"

# Runs local dev server, assets, and worker in parallel (requires Redis)
[group('Local Development')]
local-all-with-worker: _ensure-deps
    bunx concurrently --kill-others \
        --names "web,assets,worker" \
        --prefix-colors "blue,green,yellow" \
        "just local-dev-auto" \
        "bun dev" \
        "just worker-dev"
