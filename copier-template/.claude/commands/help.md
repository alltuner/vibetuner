---
name: help
description: List all available Claude commands
allowed-tools: Bash(ls:*), Bash(grep:*), Bash(cat:*)
---

# Available Commands

Here are all available Claude commands in this project:

!ls -1 /Users/dpoblador/repos/scaffolding/template/.claude/commands/*.md | sed 's|.*/||; s|\.md$||' | sort

Let me show you what each command does:

!for file in /Users/dpoblador/repos/scaffolding/template/.claude/commands/*.md; do echo ""; echo "## /$(basename "$file" .md)"; grep "^description:" "$file" | sed 's/description: //'; done

**Usage:**

- Type `/` followed by any command name (e.g., `/dev`, `/commit`, `/deploy`)
- Some commands take arguments (e.g., `/deploy papaya`, `/release-patch feature-name`)
- Commands with `<required>` arguments must include the parameter
- Commands with `[optional]` arguments can be used with or without parameters

**Quick Reference:**

- **Development**: `/dev` - Start development environment
- **Code Quality**: `/format` - Format and lint all code  
- **Git Operations**: `/commit`, `/commit-all` - Smart commit with generated messages
- **Releases**: `/release-patch <branch>`, `/release-minor <branch>` - Complete release workflow
- **Dependencies**: `/update-deps` - Update and commit all dependencies
- **Deployment**: `/deploy <environment>` - Deploy to specified environment
- **Testing**: `/auth-test` - Open app in browser for authentication testing
- **Maintenance**: `/update-scaffolding` - Update project scaffolding

For detailed information about any command, you can also check the command files in `.claude/commands/`.
