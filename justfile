PYTHON_VERSION := `cat .python-version`

COMPOSE_DEV := "compose.dev.yml"
COMPOSE_PROD := "compose.prod.yml"

# Gracefully fallback if no tags exist
LATEST_VERSION_TAG := `git describe --tags --abbrev=0 --match "v*" 2>/dev/null | sed 's/^v//' || echo "0.0.0"`
VERSION := `uvx dunamai from git 2>/dev/null || echo 0.0.0`

# List available commands
default:
    @just --list

# Runs the dev environment with watch mode and cleans up orphans
dev:
    ENVIRONMENT=development \
    PYTHON_VERSION={{PYTHON_VERSION}} \
    COMPOSE_BAKE=true \
    docker compose -f {{COMPOSE_DEV}} up --watch --remove-orphans

# Builds the dev image with COMPOSE_BAKE set
build-dev:
    ENVIRONMENT=development \
    PYTHON_VERSION={{PYTHON_VERSION}} \
    COMPOSE_BAKE=true \
    docker compose -f {{COMPOSE_DEV}} build

check-clean:
    @git diff --quiet || (echo "❌ Uncommitted changes found. Commit or stash them before building." && exit 1)
    @git diff --cached --quiet || (echo "❌ Staged but uncommitted changes found. Commit them before building." && exit 1)

check-unpushed-commits:
    @git fetch origin > /dev/null
    @commits=`git rev-list HEAD ^origin/HEAD --count`; \
    if [ "$commits" -ne 0 ]; then \
        echo "❌ You have local commits that haven't been pushed."; \
        exit 1; \
    fi

check-last-commit-tagged:
    @if [ -z "$(git tag --points-at HEAD)" ]; then \
        echo "❌ Current commit is not tagged."; \
        echo "   Please checkout a clean tag before building production."; \
        exit 1; \
    fi

# Builds the prod image with COMPOSE_BAKE set (only if on a clean, tagged commit)
release: check-clean check-unpushed-commits check-last-commit-tagged
    ENVIRONMENT=production \
    PYTHON_VERSION={{PYTHON_VERSION}} \
    VERSION={{VERSION}} \
    docker buildx bake -f {{COMPOSE_PROD}} --push

bump-major:
    @just bump major

bump-minor:
    @just bump minor

bump-patch:
    @just bump patch

# Internal recipe to bump version and create git tag
bump type: check-clean check-unpushed-commits
    #!/usr/bin/env bash
    if ! git tag | grep -q '^v'; then
        echo "No version tags found. Creating initial tag v0.0.1..."
        git tag -a "v0.0.1" -m "Initial version"
        echo "Created git tag: v0.0.1"
        echo "To push the tag, run: git push origin v0.0.1"
        exit 0
    fi

    NEW_VERSION=$(uvx --from semver pysemver bump {{type}} {{LATEST_VERSION_TAG}})
    if [ -z "$NEW_VERSION" ]; then
        echo "❌ Failed to compute new version. Aborting to avoid invalid tag."
        exit 1
    fi

    echo "New version: $NEW_VERSION"

    TAG="v${NEW_VERSION}"

    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "Tag $TAG already exists. Skipping tag creation."
    else
        echo "Creating git tag $TAG..."
        git tag -a "$TAG" -m "Version $NEW_VERSION"
        echo "Created git tag: $TAG"
        echo "To push the tag, run: git push origin $TAG"
    fi

start-branch BRANCH: check-clean check-unpushed-commits
    git checkout main
    git pull origin main
    git checkout -b {{BRANCH}}

# Commit changes with a message
commit MESSAGE:
    git add .
    git commit -m "{{MESSAGE}}"

pr:
    @git push

    @branch=$(git rev-parse --abbrev-ref HEAD) && \
    gh pr create \
      --base main \
      --title "$branch" \
      --body "$(git log origin/main..HEAD --pretty=format:'- %s')"


# Merge PR using squash
merge:
    gh pr merge --squash --delete-branch
