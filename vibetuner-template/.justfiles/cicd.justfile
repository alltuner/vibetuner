# ABOUTME: CI/CD recipes for building, releasing, and deploying Docker images.
# ABOUTME: PUSH_REGISTRY overrides DOCKER_REGISTRY for fast local pushes.

import 'helpers.justfile'

# Builds the dev image with COMPOSE_BAKE set
[group('CI/CD')]
build-dev: install-deps
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=dev COMPOSE_BAKE=true \
    docker compose --progress=plain -f compose.dev.yml build

# Test-builds the prod image locally
[group('CI/CD')]
test-build-prod: install-deps
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=prod docker buildx bake -f compose.prod.yml

# Builds the prod image (only if on a clean, tagged commit)
[group('CI/CD')]
build-prod: _check-clean _check-last-commit-tagged install-deps
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=prod docker buildx bake -f compose.prod.yml

# Builds and pushes the prod image (only if on a clean, tagged commit).
# PUSH_REGISTRY overrides DOCKER_REGISTRY for fast local pushes.
[group('CI/CD')]
release: _check-clean _check-last-commit-tagged
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    if [ -n "${PUSH_REGISTRY:-}" ]; then
        export DOCKER_REGISTRY="$PUSH_REGISTRY"
    fi
    ENVIRONMENT=prod docker buildx bake -f compose.prod.yml --push

# Deploys to a remote host, pulling from the configured registry.
[group('CI/CD')]
deploy-latest HOST:
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    DOCKER_HOST="ssh://{{ HOST }}" ENVIRONMENT=prod \
    docker compose -f compose.prod.yml up -d --remove-orphans --pull always
