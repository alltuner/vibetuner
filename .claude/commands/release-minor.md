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

!just pr && just merge && just bump-minor && just push-tags && just start-branch current-scaffolding

This workflow:
- `just pr` → Create and push pull request
- `just merge` → Merge the pull request 
- `just bump-minor` → Increment minor version and create git tag
- `just push-tags` → Push tags to remote
- `just start-branch current-scaffolding` → Start new current-scaffolding branch

**Perfect for:** New features, template enhancements, dependency updates

The release will be tagged and ready for users to update their projects.