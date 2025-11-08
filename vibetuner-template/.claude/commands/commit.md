---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*), Bash(ruff:*), Bash(uv:*), Bash(djlint:*), Bash(markdownlint:*)
description: Generate and create commit with relevant message for staged changes
---

# Commit Generator

I'll analyze your staged changes and create a commit with an appropriate message.

Let me check what's currently staged and generate a relevant commit message:

!git status && git diff --cached && git log --oneline -5

Based on the staged changes, I'll analyze:

- What files have been modified
- The nature of the changes (new features, bug fixes, refactoring, etc.)
- Recent commit message patterns for consistency

Then I'll create a commit with a message that:

- Summarizes the changes concisely
- Follows conventional commit format when appropriate
- Includes the Claude Code footer for attribution

Finally, I'll run comprehensive code formatting to ensure consistency:

!ruff format . && ruff check --fix . && djlint --reformat templates/ --quiet && bun markdownlint **/*.md --fix

This command will automatically generate an appropriate commit message based on your actual changes, similar to what I did earlier with your Swedish language support changes.
