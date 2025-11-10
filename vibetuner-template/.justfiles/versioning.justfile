import 'helpers.justfile'

LATEST_VERSION_TAG := `git describe --tags --abbrev=0 --match "v*" 2>/dev/null | sed 's/^v//' || echo "0.0.0"`

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

    NEW_VERSION=$(uv run pysemver bump {{ type }} {{ LATEST_VERSION_TAG }})
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

