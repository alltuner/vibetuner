---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(ruff:*), Bash(uv:*), Bash(djlint:*), Bash(markdownlint:*)
description: Stage all changes and create commit with relevant message
---

I'll stage all your changes (both staged and unstaged) and create a commit with an appropriate message.

Let me check what's currently changed and generate a relevant commit message:

!git status && git diff && git diff --cached && git log --oneline -5

Based on all the changes (staged and unstaged), I'll analyze:

- What files have been modified, added, or deleted
- The nature of the changes (new features, bug fixes, refactoring, etc.)
- Recent commit message patterns for consistency

Then I'll:

1. 📝 Stage all changes with `git add .`
2. 🧹 Run comprehensive code formatting for consistency
3. 💾 Create a commit with a message that:
   - Summarizes the changes concisely
   - Follows conventional commit format when appropriate
   - Includes the Claude Code footer for attribution

!git add . && ruff format . && ruff check --fix . && djlint --reformat templates/ --quiet && bun markdownlint **/*.md --fix && git add .

This command captures ALL your current work (staged + unstaged) and creates a meaningful commit, perfect for saving progress or preparing for a release workflow.
