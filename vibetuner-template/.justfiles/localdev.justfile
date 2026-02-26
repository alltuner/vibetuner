import 'deps.justfile'

# Runs the dev environment with watch mode and cleans up orphans
[group('Local Development')]
dev:
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=development COMPOSE_BAKE=true \
    docker compose -f compose.dev.yml up --watch --remove-orphans

# Runs the dev environment locally without Docker
[group('Local Development')]
local-dev host="0.0.0.0":
    @DEBUG=true uv run --frozen vibetuner run dev --host {{ host }}

# Runs the task worker locally without Docker
[group('Local Development')]
worker-dev:
    @DEBUG=true uv run --frozen vibetuner run dev worker

# Runs local dev server and assets in parallel
[group('Local Development')]
local-all host="0.0.0.0": install-deps
    bunx concurrently --kill-others \
        --names "web,assets" \
        --prefix-colors "blue,green" \
        "just local-dev {{ host }}" \
        "bun dev"

# Runs local dev server, assets, and worker in parallel (requires Redis)
[group('Local Development')]
local-all-with-worker: install-deps
    bunx concurrently --kill-others \
        --names "web,assets,worker" \
        --prefix-colors "blue,green,yellow" \
        "just local-dev" \
        "bun dev" \
        "just worker-dev"
