set allow-duplicate-recipes

_default:
    @just --list

import '.justfiles/deps.justfile'
import '.justfiles/docs.justfile'
import '.justfiles/linting.justfile'
import '.justfiles/testing.justfile'
import 'vibetuner-template/.justfiles/linting.justfile'
import 'vibetuner-template/.justfiles/formatting.justfile'
