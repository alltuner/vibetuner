---
description: Create a pull request with systematic workflow
---

# Create Pull Request

Create a pull request following a systematic workflow that ensures proper branching,
conventional commits, and clean git state.

## General Rules

- Never make changes outside the current Git repository
- Use simple, explicit git and gh commands over complex scripting
- If any step fails, stop and clearly explain what happened
- Use ONLY these Conventional Commit types: `feat`, `fix`, `refactor`, `perf`, `chore`, `docs`, `ci`, `style`, `build`
- Commit messages must follow: `<type>(optional-scope): <short, imperative description>`
  - Examples: `feat: add search endpoint`, `fix(api): handle empty payloads`

## Workflow

### Step 0: Capture Initial State

Run these commands in parallel to understand the current state:

- !`git branch --show-current` - detect current branch name
- !`git status` - check for staged, unstaged, and untracked changes
- !`git log --oneline origin/main..HEAD` - check for commits not on main

**IMPORTANT**: Check if there are any release commits (e.g., "chore(main): release X.Y.Z") in the commit list. If so:

- These should NOT be on a feature branch
- You will need to rebase after creating your commit to remove them (see Step 5)
- DO NOT include release-related file changes in your commit

Assume that both staged and unstaged changes present when this command starts must be included in this PR.

### Step 1: Ensure Not Working Directly on main

**If current branch is NOT `main`:**

- Continue on the current branch

**If current branch IS `main`:**

1. Save uncommitted state: !`git stash push -u -m "claude-temp-pr-stash"`
2. Create a new branch based on `origin/main` with a clear name derived from the changes:
   - Use format: `<type>-<short-description>` (e.g., `feat-add-search`, `fix-api-error`, `chore-update-deps`)
   - Choose the type prefix based on your analysis of changes in Step 2
   - Command: !`git switch -c <branch-name> origin/main`
3. Re-apply stashed changes: !`git stash pop`
4. If conflicts occur during stash pop, STOP and explain what went wrong

### Step 2: Analyze Changes to Choose Type and Message

- Consider ALL current changes (staged and unstaged) as content for this commit
- Inspect the diff using !`git diff`, !`git diff --cached`, and !`git status`
- Based on actual changes, choose the most appropriate Conventional Commit type:
  - `feat` - new features or functionality
  - `fix` - bug fixes
  - `refactor` - code restructuring without behavior change
  - `perf` - performance improvements
  - `chore` - maintenance, dependencies, tooling
  - `docs` - documentation only
  - `ci` - CI/CD changes
  - `style` - formatting, linting
  - `build` - build system changes
- Create a clear, concise description in imperative mood (e.g., "add...", "fix...", "update...")
- Include scope in parentheses if a natural one exists (package name, directory, service), otherwise omit
- Examples:
  - `feat(api): add pagination to podcasts endpoint`
  - `chore: update devcontainer configuration`
  - `fix: resolve Docker build failure`

### Step 3: Stage and Commit

1. Stage all relevant changes:
   - **IMPORTANT**: NEVER stage release-related files: `.release-please-manifest.json`,
     `CHANGELOG.md`, version changes in `pyproject.toml` or `package.json`
   - Use !`git add` with explicit file paths for each file you want to commit
   - If you must use !`git add -A`, immediately check !`git status` and unstage any
     release-related files with !`git restore --staged <file>`
2. Verify staged changes: !`git diff --cached` should show exactly what you intend to commit
   - **VERIFY**: Ensure NO release-related files are staged
     (`.release-please-manifest.json`, `CHANGELOG.md`, version bumps)
3. Create commit with the conventional commit message: !`git commit -m "<type>(optional-scope): <description>"`
4. If no changes exist (clean index and working tree), skip this step and explain that there were no changes to commit

### Step 4: Ensure Clean Working Tree

1. Verify clean state: !`git status` should show NO staged or unstaged changes
2. If uncommitted changes remain:
   - Determine what was missed
   - Stage them with !`git add`
   - Either:
     - Amend the previous commit if they belong together: !`git commit --amend`
     - Create a new commit with proper conventional message
3. Repeat until working tree is completely clean

### Step 5: Prepare and Push the Branch

1. Fetch latest changes: !`git fetch origin`
2. Check for unwanted commits: !`git log --oneline origin/main..HEAD`
   - If there are release commits (e.g., "chore(main): release X.Y.Z"), you MUST rebase
3. Rebase onto main to clean up history: !`git rebase origin/main`
   - This will remove duplicate commits that are already on main
   - Git will skip commits that are already applied
4. Push branch to origin:
   - First push: !`git push -u origin <branch-name>`
   - After rebase: !`git push --force-with-lease origin <branch-name>`
5. If push fails (branch exists, rejected, etc.), explain and stop

### Step 6: Create the Pull Request

1. Collect commits on this branch not on `origin/main`:
   !`git log origin/main..HEAD`
2. Derive PR title:
   - If one commit: use that commit message as-is
   - If multiple commits: choose the best representative one or synthesize a clear
     title following `<type>(scope): <description>`
3. Derive PR body:
   - Short summary of WHAT changed (bullet points)
   - Optionally WHY it changed and relevant context
   - Testing or verification performed (e.g., "Tested in dev environment")
4. Create PR:
   !`gh pr create --title "<conventional-commit-style-title>" \
     --body "<multi-line description>" --base main --head <branch-name>`
5. Do NOT assign reviewers or labels unless explicitly instructed

### Step 7: Final Output

Print:

- Branch name
- Final commit message(s)
- `gh` output including PR URL

If any step failed, clearly explain:

- What failed
- Which command failed
- What should be done manually to recover

## Important Constraints

- NEVER run destructive commands (`git reset --hard`, `git push --force`,
  `git stash drop`) without explicit instruction
- ALWAYS respect the conventional commit type list: `feat`, `fix`, `refactor`,
  `perf`, `chore`, `docs`, `ci`, `style`, `build`
- ALWAYS choose the most appropriate type based on actual changes
- NEVER skip pre-commit (prek) hooks
- NEVER bypass git safety protocols
