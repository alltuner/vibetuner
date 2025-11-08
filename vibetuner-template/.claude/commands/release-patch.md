---
allowed-tools: Bash(just pr:*), Bash(just merge:*), Bash(just bump-patch:*), Bash(just push-tags:*), Bash(just start-branch:*), Bash(git:*)
argument-hint: <next-branch-name>
description: Complete release workflow with patch version increment
---

# Patch Release Creator

I'll execute your complete release workflow with **patch** version increment.

**Next branch name:** $1 (required)

Let me run through each step:

!just pr && just merge && just bump-patch && just push-tags && just start-branch $1

This workflow will:

1. 🚀 Create and push PR for current branch
2. 🔄 Squash merge the PR and delete branch  
3. 🔧 Bump **patch** version (e.g., 1.2.3 → 1.2.4) and create git tag
4. 🏷️ Push all tags to remote repository
5. 🌿 Start new development branch ($1)

**Usage examples:**

- `/release-patch feature-auth` → creates 'feature-auth' branch
- `/release-patch bugfix-login` → creates 'bugfix-login' branch

**Perfect for:** Bug fixes, small improvements, documentation updates

Each step must succeed before continuing to the next one.
