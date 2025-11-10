set allow-duplicate-recipes

_default:
    @just --list

import '.justfiles/deps.justfile'
import '.justfiles/docs.justfile'
import 'vibetuner-template/.justfiles/linting.justfile'
import 'vibetuner-template/.justfiles/formatting.justfile'

# Type check Python files with ty (disabled by ty.toml)
[group('linting')]
type-check:
    @cd vibetuner-py && uv run ty check .

# Test scaffolding with local vibetuner source (for development)
[group('development')]
test-local:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Cleaning up old test project..."
    rm -rf ./tmp/test-project
    echo "Scaffolding new project with copier..."
    copier copy -f --defaults . ./tmp/test-project
    cd ./tmp/test-project
    echo "Adding local vibetuner source override..."
    cat >> pyproject.toml << 'EOF'

    [tool.uv.sources]
    vibetuner = { path = "../../vibetuner-py", editable = true }
    EOF
    echo "Syncing dependencies with local vibetuner..."
    uv sync
    echo "Starting development environment..."
    just dev

################################################################################
# The following includes are relevant for the scaffolded projects, but not for #
# the root repo as we already incorporate solid CI/CD practices.               #
################################################################################
# import 'vibetuner-template/.justfiles/gitflow.justfile'
# import 'vibetuner-template/.justfiles/versioning.justfile'
