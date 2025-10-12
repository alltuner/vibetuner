---
name: commit
description: Commit all staged and unstaged changes with a descriptive message
allowed-tools: Bash(git:*)
---

# Commit All Changes

I'll commit all changes with a proper commit message.

Let me check the current status and create an appropriate commit:

!git status && git add . && git diff --cached --stat

Now I'll create a commit with a descriptive message based on the changes:

!git commit -m "$(cat <<'EOF'
Add Claude Code release commands for scaffolding template

- Add /release-patch command for patch version releases
- Add /release-minor command for minor version releases  
- Create .claude/commands/ directory structure
- Simple inline commands without specialized agents

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

This will:

- Stage all modified and new files with `git add .`
- Create a descriptive commit message explaining the changes
- Include the Claude Code signature as per project conventions
