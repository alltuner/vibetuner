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
    @:

################################################################################
# The following includes are relevant for the scaffolded projects, but not for #
# the root repo as we already incorporate solid CI/CD practices.               #
################################################################################
# import 'vibetuner-template/.justfiles/gitflow.justfile'
# import 'vibetuner-template/.justfiles/versioning.justfile'
