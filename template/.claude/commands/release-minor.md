---
allowed-tools: Bash(just pr:*), Bash(just merge:*), Bash(just bump-minor:*), Bash(just push-tags:*), Bash(just start-branch:*), Bash(git:*)
argument-hint: <next-branch-name>
description: Complete release workflow with minor version increment
---

I'll execute your complete release workflow with **minor** version increment.

**Next branch name:** $1 (required)

Let me run through each step:

!just pr && just merge && just bump-minor && just push-tags && just start-branch $1

This workflow will:

1. 🚀 Create and push PR for current branch
2. 🔄 Squash merge the PR and delete branch  
3. 📈 Bump **minor** version (e.g., 1.2.0 → 1.3.0) and create git tag
4. 🏷️ Push all tags to remote repository
5. 🌿 Start new development branch ($1)

**Usage examples:**

- `/release-minor feature-dashboard` → creates 'feature-dashboard' branch
- `/release-minor api-v2` → creates 'api-v2' branch

Each step must succeed before continuing to the next one.
