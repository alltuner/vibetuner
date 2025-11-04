# Vibetuner Scaffolding Project Management
# Commands for version management and releases

import 'copier-template/base.justfile'

# List all available commands
default:
    @just --list

# Sync Python dependencies in vibetuner-py
[group('Dependencies')]
sync-py:
    cd vibetuner-py && uv sync

# Sync JavaScript dependencies in vibetuner-js
[group('Dependencies')]
sync-js:
    cd vibetuner-js && bun install

# Sync all dependencies (scaffolding packages)
[group('Dependencies')]
sync: sync-py sync-js

# Test scaffold command locally
[group('Scaffolding')]
test-scaffold:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf /tmp/vibetuner-test
    uv run --directory vibetuner-py vibetuner scaffold new /tmp/vibetuner-test --defaults
    echo "Test project created at /tmp/vibetuner-test"
    echo "To test: cd /tmp/vibetuner-test && just dev"

# Clean test artifacts
[group('Scaffolding')]
clean:
    rm -rf /tmp/vibetuner-test
    rm -rf vibetuner-py/dist
    rm -rf vibetuner-js/*.tgz
    rm -rf _site

# Serve documentation locally with live reload
[group('Documentation')]
docs-serve:
    #!/usr/bin/env bash
    set -euo pipefail
    cd vibetuner-py && uv sync --group docs
    cd ..
    vibetuner-py/.venv/bin/mkdocs serve

# Build documentation
[group('Documentation')]
docs-build:
    #!/usr/bin/env bash
    set -euo pipefail
    cd vibetuner-py && uv sync --group docs
    cd ..
    vibetuner-py/.venv/bin/mkdocs build --site-dir _site

# Deploy documentation (triggers automatically on tag push, use this for manual testing)
[group('Documentation')]
docs-deploy:
    @echo "Documentation is deployed automatically on tag push to GitHub Pages"
    @echo "For manual deployment, push a tag: git tag v0.0.x && git push origin v0.0.x"
    @echo "Or manually trigger the workflow at: https://github.com/alltuner/vibetuner/actions/workflows/docs.yml"
