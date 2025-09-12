---
name: update-deps
description: Update all project dependencies (Python and Node.js)
allowed-tools: Bash(uv:*), Bash(bun:*), Bash(git:*), Bash(ruff:*)
---

I'll update all project dependencies for both Python and Node.js.

This command will:

1. 🐍 **Update Python dependencies** (equivalent to uvlu shell alias):
   - Update all Python packages to their latest compatible versions
   - Sync the environment to ensure consistency

2. 📦 **Update Node.js dependencies**:
   - Update all bun packages to their latest versions

3. ✅ **Verify updates**:
   - Show what was updated
   - Ensure all dependencies are properly synchronized

Let me run the dependency updates:

!uv lock --upgrade && uv sync && bun update

Now I'll commit the updated dependency files:

!git add uv.lock bun.lockb pyproject.toml package.json && ruff format . && git add . && git status && git diff --cached

Based on the changes, I'll create a commit with an appropriate message summarizing the dependency updates.

This will:

- `uv lock --upgrade` → Update Python dependency versions in uv.lock
- `uv sync` → Synchronize the virtual environment with updated dependencies  
- `bun update` → Update all Node.js packages to latest versions
- `git add` → Stage all dependency-related files (uv.lock, bun.lockb, pyproject.toml, package.json)
- `ruff format` → Format any code changes and stage them
- `git commit` → Commit with a descriptive message about the dependency updates

**Files that get committed:**

- `uv.lock` - Updated Python dependency versions
- `bun.lockb` - Updated Node.js dependency versions  
- `pyproject.toml` - If dependency constraints were updated
- `package.json` - If Node.js dependency versions were updated

**Safe to run:** This only updates to compatible versions within the constraints defined in your dependency files, then commits the changes with a clear message.
