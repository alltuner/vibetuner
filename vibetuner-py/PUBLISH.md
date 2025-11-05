# Publishing vibetuner to PyPI

This package is automatically published to PyPI when a GitHub release is created.

## Publishing Process

1. **Create a GitHub Release**
   - Go to <https://github.com/alltuner/vibetuner/releases/new>
   - Choose or create a tag (e.g., `v1.0.0`)
   - Write release notes
   - Optionally save as draft to review first
   - Click "Publish release"

2. **Automatic Publishing**
   - GitHub Actions workflow triggers on release publish
   - Version is extracted from the release tag
   - Package is built using `uv build`
   - Published to PyPI as `vibetuner`

3. **Version Scheme**
   - Uses unified versioning across all packages in the monorepo
   - Release tag `v1.0.0` → PyPI version `1.0.0`
   - All packages share the same version number

## Manual Publishing (if needed)

If you need to publish manually:

```bash
cd vibetuner-py

# Update version in pyproject.toml
# Then build and publish
uv build
uv publish
```

## Requirements

- PyPI account credentials configured as `PYPI_TOKEN` secret in GitHub
- Token must have permissions to publish to the `vibetuner` package

## Notes

- Version in `pyproject.toml` is automatically updated during CI
- Package has no actual code - it's a dependency bundle
- Uses hatchling as build backend
