---
allowed-tools: Bash(just update-scaffolding:*), Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*)
description: Update project scaffolding to latest version and commit changes
---

# Scaffolding Updater

I'll update your project scaffolding to the latest version and handle any changes.

First, let me check if there are any uncommitted changes that need to be stashed:

!git status

If there are uncommitted changes, I'll stash them temporarily, then run the scaffolding update:

!just update-scaffolding

After the scaffolding update completes, I'll:

1. 🔍 Check what files were updated by the scaffolding
2. 📋 Show you the changes made
3. 🔍 Check if there are any merge conflicts or pending merges
4. 💾 If clean (no merges pending), automatically commit scaffolding changes
5. 🔄 Restore any previously stashed changes

!git status && git diff --name-only

If scaffolding made changes and there are **no merge conflicts or pending merges**, I'll automatically commit them with a relevant message based on the actual changes, such as:

- "Update scaffolding to version X.Y.Z"
- "Scaffolding updates: dependency bumps and configuration changes"
- "Update project scaffolding: [specific changes detected]"

If there are merge conflicts or pending merges, I'll show you the changes but leave them uncommitted for your review.

This ensures your scaffolding stays up-to-date while safely handling the commit process and preserving your local work.
