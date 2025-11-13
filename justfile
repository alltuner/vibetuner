set allow-duplicate-recipes

_default:
    @just --list

import '.justfiles/deps.justfile'
import '.justfiles/docs.justfile'
import '.justfiles/linting.justfile'
import 'vibetuner-template/.justfiles/linting.justfile'
import 'vibetuner-template/.justfiles/formatting.justfile'

# Sync frontend templates and commit only those changes
update-frontend-templates:
    @echo "🔄 Syncing frontend templates..."
    mkdir -p vibetuner-template/core-frontend-templates
    rsync -av --delete vibetuner-py/src/vibetuner/templates/frontend/ vibetuner-template/core-frontend-templates/
    echo "✅ Templates synced."

    @echo "🪶 Adding and committing changes..."
    git add vibetuner-template/core-frontend-templates
    git commit -m "chore: update templates for Tailwind detector" -- vibetuner-template/core-frontend-templates >/dev/null 2>&1 || true

################################################################################
# The following includes are relevant for the scaffolded projects, but not for #
# the root repo as we already incorporate solid CI/CD practices.               #
################################################################################
# import 'vibetuner-template/.justfiles/gitflow.justfile'
# import 'vibetuner-template/.justfiles/versioning.justfile'
