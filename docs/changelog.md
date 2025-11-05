# Changelog

This page contains the complete changelog for the Vibetuner project.

## 📋 Complete Changelog

For the full changelog with all version history, release notes, and package-specific changes, see the **[main CHANGELOG.md](https://github.com/alltuner/vibetuner/blob/main/CHANGELOG.md)** file in the repository.

## 🔄 How Updates Are Managed

Vibetuner uses **Release Please** for automated changelog management:

1. **PR Titles**: Contributors use conventional commit format (e.g., `feat: add OAuth support`)
2. **Automatic Detection**: Release Please analyzes PR titles to categorize changes
3. **Smart Versioning**: Determines MAJOR/MINOR/PATCH versions automatically
4. **Professional Notes**: Generates clean, organized changelog entries
5. **Package Awareness**: Groups changes by affected packages

## 📦 Package-Specific Changes

The main changelog includes changes for all Vibetuner components:

- **Python Package** (`vibetuner`): Core framework and CLI tools
- **JavaScript Package** (`@alltuner/vibetuner`): Frontend dependencies
- **Scaffolding Template**: Project template and configuration

Changes are automatically categorized by which packages were affected in each release.

## 🤝 Contributing to Changelog

When contributing to Vibetuner, please follow the [PR title guidelines](../CONTRIBUTING.md#pr-title-format-important) to ensure proper changelog generation.

### Quick Reference

```bash
# New Features → MINOR release
feat: add new feature
feat(scope): specific feature

# Bug Fixes → PATCH release  
fix: resolve issue
fix(scope): specific fix

# Breaking Changes → MAJOR release
feat!: breaking change
BREAKING CHANGE: description

# Documentation → PATCH release
docs: update documentation

# Maintenance → PATCH release
chore: update dependencies
refactor: improve code structure
```

## 🔗 Related Links

- **[Main Changelog](https://github.com/alltuner/vibetuner/blob/main/CHANGELOG.md)** – Complete version history
- **[GitHub Releases](https://github.com/alltuner/vibetuner/releases)** – Release downloads and notes
- **[Contributing Guidelines](../CONTRIBUTING.md)** – How to contribute
- **[Agent Guidance](../AGENTS.md)** – Guidelines for AI assistants

---

*This changelog system ensures transparent, professional release notes while maintaining development efficiency.*
