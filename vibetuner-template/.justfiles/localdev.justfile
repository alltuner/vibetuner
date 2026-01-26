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
    @DEBUG=true vibetuner run dev --port {{ PORT }}

# Runs local dev with auto-assigned port (deterministic per project path)
[group('Local Development')]
local-dev-auto: install-deps
    @DEBUG=true vibetuner run dev --auto-port

# Runs the task worker locally without Docker
[group('Local Development')]
worker-dev: install-deps
    @DEBUG=true vibetuner run dev worker

# Runs local dev server and assets in parallel (auto-port)
[group('Local Development')]
local-all: install-deps
    bunx concurrently --kill-others \
        --names "web,assets" \
        --prefix-colors "blue,green" \
        "just local-dev-auto" \
        "bun dev"

# Runs local dev server, assets, and worker in parallel (requires Redis)
[group('Local Development')]
local-all-with-worker: install-deps
    bunx concurrently --kill-others \
        --names "web,assets,worker" \
        --prefix-colors "blue,green,yellow" \
        "just local-dev-auto" \
        "bun dev" \
        "just worker-dev"

# Notify vibetuner app of Claude Code events (called by Claude hooks)
[group('Local Development')]
claude-notify:
    @uv run vibetuner notify 2>/dev/null || true
