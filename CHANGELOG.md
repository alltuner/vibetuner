# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.12.1](https://github.com/alltuner/vibetuner/compare/v2.12.0...v2.12.1) (2025-11-05)


### Bug Fixes

* update PR title validation to support breaking changes and upgrade action ([#334](https://github.com/alltuner/vibetuner/issues/334)) ([2464200](https://github.com/alltuner/vibetuner/commit/24642009e8d15f891a85e574c50f5cb303379a4d))

## [2.12.0](https://github.com/alltuner/vibetuner/compare/v2.11.0...v2.12.0) (2025-11-05)


### Features

* enable automatic GitHub releases on PR merge ([#338](https://github.com/alltuner/vibetuner/issues/338)) ([e759ec1](https://github.com/alltuner/vibetuner/commit/e759ec1398acc678257eb9698ef4c4a21da4c7ac))
* implement automated changelog management with Release Please ([#333](https://github.com/alltuner/vibetuner/issues/333)) ([c498374](https://github.com/alltuner/vibetuner/commit/c4983741d87fbabcbd89e496860712d6d793eba2))


### Bug Fixes

* resolve Release Please workflow issues and improve commit validation ([#335](https://github.com/alltuner/vibetuner/issues/335)) ([57cebfe](https://github.com/alltuner/vibetuner/commit/57cebfed0fc03a1b32b534f2e738d4ced7efaa42))

## [Unreleased]

### Added

- Automated changelog management with Release Please
- PR title validation for conventional commit format
- Enhanced package publishing with smart change detection
- Changelog integration in documentation and package metadata

### Changed

- Updated contribution guidelines with PR title requirements
- Added AI assistant guidance for PR titles
- Improved documentation navigation

### Infrastructure

- Added Release Please configuration for automated releases
- Enhanced GitHub workflows for better release management

---

## [Previous Versions]

This changelog is managed automatically by [Release Please](https://github.com/googleapis/release-please).

For versions prior to automated changelog management, please check the [GitHub releases page](https://github.com/alltuner/vibetuner/releases).

---

## Package-Specific Changes

This changelog covers changes across all Vibetuner components:

- **Python Package** (`vibetuner`): Core framework and CLI tools
- **JavaScript Package** (`@alltuner/vibetuner`): Frontend dependencies
- **Scaffolding Template**: Project template and configuration

Changes are automatically categorized by which packages were affected.

---

## How This Chelog is Generated

1. **PR Titles**: Contributors use conventional commit format in PR titles
2. **Release Please**: Analyzes PR titles to categorize changes
3. **Automatic Generation**: Creates professional changelog entries
4. **Package Detection**: Groups changes by affected packages

See [CONTRIBUTING.md](./CONTRIBUTING.md) for PR title guidelines.
