---
name: release-patch
description: Release a new patch version of the scaffolding template
allowed-tools: Bash(just:*), Bash(git:*)
---

I'll create a patch release of the scaffolding template.

This will:
1. 🔧 Bump patch version (e.g., 1.2.3 → 1.2.4)
2. 🏷️ Create and push git tag
3. 🚀 Create GitHub pull request

Let me execute the release workflow:

!just bump-patch && just pr

This workflow:
- `just bump-patch` → Increments patch version and creates git tag
- `just pr` → Pushes current branch and creates GitHub pull request

**Perfect for:** Bug fixes, documentation updates, minor template improvements

The release will be tagged and ready for users to update their projects.