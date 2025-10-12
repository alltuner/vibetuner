---
name: release-patch
description: Release a new patch version of the scaffolding template
allowed-tools: Bash(just:*), Bash(git:*)
---

# Patch Release Creator

I'll create a patch release of the scaffolding template.

This will:

1. 🔧 Bump patch version (e.g., 1.2.3 → 1.2.4)
2. 🏷️ Create and push git tag
3. 🚀 Create GitHub pull request

Let me execute the release workflow:

!just pr && just merge && just bump-patch && just push-tags && just start-branch current-scaffolding

This workflow:

- `just pr` → Create and push pull request
- `just merge` → Merge the pull request
- `just bump-patch` → Increment patch version and create git tag
- `just push-tags` → Push tags to remote
- `just start-branch current-scaffolding` → Start new current-scaffolding branch

**Perfect for:** Bug fixes, documentation updates, minor template improvements

The release will be tagged and ready for users to update their projects.
