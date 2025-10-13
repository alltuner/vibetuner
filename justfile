# Gracefully fallback if no tags exist
LATEST_VERSION_TAG := `git describe --tags --abbrev=0 --match "v*" 2>/dev/null | sed 's/^v//' || echo "0.0.0"`

# List available commands
default:
    @just --list

[group('Helpers')]
_check-clean:
    @git diff --quiet || (echo "❌ Uncommitted changes found. Commit or stash them before building." && exit 1)
    @git diff --cached --quiet || (echo "❌ Staged but uncommitted changes found. Commit them before building." && exit 1)

[group('Helpers')]
_check-unpushed-commits:
    @git fetch origin > /dev/null
    @commits=`git rev-list HEAD ^origin/HEAD --count`; \
    if [ "$commits" -ne 0 ]; then \
        echo "❌ You have local commits that haven't been pushed."; \
        exit 1; \
    fi

[group('Helpers')]
_check-last-commit-tagged:
    @if [ -z "$(git tag --points-at HEAD)" ]; then \
        echo "❌ Current commit is not tagged."; \
        echo "   Please checkout a clean tag before building production."; \
        exit 1; \
    fi

# Bump major version based on the latest tag
[group('versioning')]
bump-major:
    @just _semver_bump major

# Bump minor version based on the latest tag
[group('versioning')]
bump-minor:
    @just _semver_bump minor

# Bump patch version based on the latest tag
[group('versioning')]
bump-patch:
    @just _semver_bump patch

# Internal recipe to bump version and create git tag
[group('versioning')]
_semver_bump type: _check-clean _check-unpushed-commits
    #!/usr/bin/env bash
    if ! git tag | grep -q '^v'; then
        echo "No version tags found. Creating initial tag v0.0.1..."
        git tag -a "v0.0.1" -m "Initial version"
        echo "Created git tag: v0.0.1"
        echo "To push the tag, run: git push origin v0.0.1"
        exit 0
    fi

    NEW_VERSION=$(pysemver bump {{type}} {{LATEST_VERSION_TAG}})
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

# Starts a new branch for development
[group('gitflow')]
start-branch BRANCH: _check-clean _check-unpushed-commits
    git checkout main
    git pull origin main
    git checkout -b {{BRANCH}}

# Adds and commits all changes with a message
[group('gitflow')]
commit MESSAGE:
    git add .
    git commit -m "{{MESSAGE}}"

# Pushes all tags to the remote repository
[group('gitflow')]
push-tags:
    git push --tags

# Create PR for current branch
[group('gitflow')]
pr:
    @git push

    @branch=$(git rev-parse --abbrev-ref HEAD) && \
    gh pr create \
      --base main \
      --title "$branch" \
      --body "$(git log origin/main..HEAD --pretty=format:'- %s')"


# Merge PR using squash
[group('gitflow')]
merge:
    gh pr merge --squash --delete-branch

# Lint markdown files including dot directories
[group('linting')]
lint-md:
    uv run rumdl check . .claude .github template template/.*

# Lint Python files with ruff
[group('linting')]
lint-py:
    uv run ruff check .

# Type check Python files with ty (disabled by ty.toml)
[group('linting')]
type-check:
    uv run ty check .

# Run all linting checks
[group('linting')]
lint: lint-md lint-py
