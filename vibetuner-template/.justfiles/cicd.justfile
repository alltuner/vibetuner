import 'helpers.justfile'

# Builds the dev image with COMPOSE_BAKE set
[group('CI/CD')]
build-dev: install-deps
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=dev \
    COMPOSE_BAKE=true \
    PYTHON_VERSION=$PYTHON_VERSION \
    COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME \
    docker compose --progress=plain -f compose.dev.yml build

# Test-builds the prod image locally
[group('CI/CD')]
test-build-prod: install-deps
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=prod \
    PYTHON_VERSION=$PYTHON_VERSION \
    COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME \
    FQDN=$FQDN \
    ENABLE_WATCHTOWER=$ENABLE_WATCHTOWER \
    docker buildx bake -f compose.prod.yml

# Builds the prod image (only if on a clean, tagged commit)
[group('CI/CD')]
build-prod: _check-clean _check-last-commit-tagged install-deps
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=prod \
    VERSION=$VERSION \
    PYTHON_VERSION=$PYTHON_VERSION \
    COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME \
    FQDN=$FQDN \
    ENABLE_WATCHTOWER=$ENABLE_WATCHTOWER \
    docker buildx bake -f compose.prod.yml

# Builds and pushes the prod image (only if on a clean, tagged commit)
[group('CI/CD')]
release: _check-clean _check-last-commit-tagged
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    ENVIRONMENT=prod \
    VERSION=$VERSION \
    PYTHON_VERSION=$PYTHON_VERSION \
    COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME \
    FQDN=$FQDN \
    ENABLE_WATCHTOWER=$ENABLE_WATCHTOWER \
    docker buildx bake -f compose.prod.yml --push

# Releases and deploys to a remote host
[group('CI/CD')]
deploy-latest HOST: release
    #!/usr/bin/env bash
    set -euo pipefail
    eval "$(just _project-vars)"
    DOCKER_HOST="ssh://{{ HOST }}" \
    ENVIRONMENT=prod \
    VERSION=$VERSION \
    PYTHON_VERSION=$PYTHON_VERSION \
    COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME \
    FQDN=$FQDN \
    ENABLE_WATCHTOWER=$ENABLE_WATCHTOWER \
    docker compose -f compose.prod.yml up -d --remove-orphans --pull always
