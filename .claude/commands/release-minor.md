---
name: release-minor
description: Release a new minor version of the scaffolding template
allowed-tools: Bash(just:*), Bash(git:*)
---

I'll create a minor release of the scaffolding template.

This will:
1. 🔧 Bump minor version (e.g., 1.2.3 → 1.3.0)
2. 🏷️ Create and push git tag
3. 🚀 Create GitHub pull request

Let me execute the release workflow:

!just bump-minor && just pr

This workflow:
- `just bump-minor` → Increments minor version and creates git tag
- `just pr` → Pushes current branch and creates GitHub pull request

**Perfect for:** New features, template enhancements, dependency updates

The release will be tagged and ready for users to update their projects.