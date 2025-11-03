# Publishing @alltuner/vibetuner to npm

The `@alltuner/vibetuner` package is automatically published to npm when a git tag matching `js-v*` is pushed.

## Publishing a New Version

1. **Decide on the version number** (following semver):
   - Patch release (bug fixes): `1.0.1`
   - Minor release (new features, backward compatible): `1.1.0`
   - Major release (breaking changes): `2.0.0`

2. **Create and push a git tag**:

   ```bash
   # Example for version 1.0.0
   git tag js-v1.0.0
   git push origin js-v1.0.0
   ```

3. **GitHub Actions will automatically**:
   - Extract the version from the tag (e.g., `js-v1.0.0` → `1.0.0`)
   - Update `package.json` with the version
   - Install dependencies with bun
   - Publish to npm registry

## Prerequisites

The repository must have an `NPM_TOKEN` secret configured:

1. Generate an npm token at <https://www.npmjs.com/settings/YOUR_USERNAME/tokens>
2. Add it as a repository secret named `NPM_TOKEN`

## Tag Format

Tags **must** follow the format: `js-v{MAJOR}.{MINOR}.{PATCH}`

Examples:

- ✅ `js-v1.0.0`
- ✅ `js-v1.2.3`
- ✅ `js-v2.0.0-beta.1`
- ❌ `v1.0.0` (missing `js-` prefix)
- ❌ `1.0.0` (missing `js-v` prefix)

## Checking Published Versions

View published versions on npm:

```bash
npm view @alltuner/vibetuner versions
```

Or visit: <https://www.npmjs.com/package/@alltuner/vibetuner>

## Manual Publishing (Not Recommended)

If you need to publish manually:

```bash
cd vibetuner-js

# Update version in package.json
bun run --bun -e "
  const fs = require('fs');
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  pkg.version = '1.0.0';
  fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
"

# Install dependencies
bun install

# Publish (requires npm login)
bun publish --access public
```
