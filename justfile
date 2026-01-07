set allow-duplicate-recipes

_default:
    @just --list

import '.justfiles/deps.justfile'
import '.justfiles/docs.justfile'
import '.justfiles/gitflow.justfile'
import '.justfiles/linting.justfile'
import '.justfiles/testing.justfile'
import 'vibetuner-template/.justfiles/linting.justfile'
import 'vibetuner-template/.justfiles/formatting.justfile'

################################################################################
# The following includes are relevant for the scaffolded projects, but not for #
# the root repo as we already incorporate solid CI/CD practices.               #
################################################################################
# import 'vibetuner-template/.justfiles/gitflow.justfile'
# import 'vibetuner-template/.justfiles/versioning.justfile'
