import 'helpers.justfile'

PYTHON_VERSION := `tr -d '\n\r' < .python-version`
VERSION := `uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"`
PROJECT_SLUG := `uv run python -c "import yaml, os; p='.copier-answers.yml'; print((yaml.safe_load(open(p)) if os.path.exists(p) else {}).get('project_slug', 'scaffolding').strip())"`
FQDN := `uv run python -c "import yaml, os, sys; p='.copier-answers.yml'; print((yaml.safe_load(open(p)) if os.path.exists(p) else {}).get('fqdn', '').strip()) if os.path.exists(p) else print('')"`
ENABLE_WATCHTOWER := `uv run python -c "import yaml, os, sys; p='.copier-answers.yml'; print(str((yaml.safe_load(open(p)) if os.path.exists(p) else {}).get('enable_watchtower', False)).lower()) if os.path.exists(p) else print('false')"`

# Builds the dev image with COMPOSE_BAKE set
[group('CI/CD')]
build-dev: install-deps
    ENVIRONMENT=dev \
    COMPOSE_BAKE=true \
    PYTHON_VERSION={{ PYTHON_VERSION }} \
    COMPOSE_PROJECT_NAME={{ PROJECT_SLUG }} \
    docker compose --progress=plain -f compose.dev.yml build

# Builds the prod image with COMPOSE_BAKE set (only if on a clean, tagged commit)
[group('CI/CD')]
test-build-prod: install-deps
    ENVIRONMENT=prod \
    PYTHON_VERSION={{ PYTHON_VERSION }} \
    COMPOSE_PROJECT_NAME={{ PROJECT_SLUG }} \
    FQDN={{ FQDN }} \
    ENABLE_WATCHTOWER={{ ENABLE_WATCHTOWER }} \
    docker buildx bake -f compose.prod.yml

# Builds the prod image with COMPOSE_BAKE set (only if on a clean, tagged commit)
[group('CI/CD')]
build-prod: _check-clean _check-last-commit-tagged install-deps
    ENVIRONMENT=prod \
    VERSION={{ VERSION }} \
    PYTHON_VERSION={{ PYTHON_VERSION }} \
    COMPOSE_PROJECT_NAME={{ PROJECT_SLUG }} \
    FQDN={{ FQDN }} \
    ENABLE_WATCHTOWER={{ ENABLE_WATCHTOWER }} \
    docker buildx bake -f compose.prod.yml

# Builds the prod image with COMPOSE_BAKE set (only if on a clean, tagged commit)
[group('CI/CD')]
release: _check-clean _check-last-commit-tagged
    ENVIRONMENT=prod \
    VERSION={{ VERSION }} \
    PYTHON_VERSION={{ PYTHON_VERSION }} \
    COMPOSE_PROJECT_NAME={{ PROJECT_SLUG }} \
    FQDN={{ FQDN }} \
    ENABLE_WATCHTOWER={{ ENABLE_WATCHTOWER }} \
    docker buildx bake -f compose.prod.yml --push

# Builds the prod image with COMPOSE_BAKE set (only if on a clean, tagged commit)
[group('CI/CD')]
deploy-latest HOST: release
    DOCKER_HOST="ssh://{{ HOST }}" \
    PYTHON_VERSION={{ PYTHON_VERSION }} \
    VERSION={{ VERSION }} \
    COMPOSE_PROJECT_NAME={{ PROJECT_SLUG }} \
    FQDN={{ FQDN }} \
    ENABLE_WATCHTOWER={{ ENABLE_WATCHTOWER }} \
    docker compose -f compose.prod.yml up -d --remove-orphans --pull always
