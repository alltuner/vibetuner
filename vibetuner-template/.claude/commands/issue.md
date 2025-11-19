---
argument-hint: [issue-number]
description: Work on a GitHub issue with systematic workflow
allowed-tools: Bash(git:*), Bash(gh:*), TodoWrite, Read, Edit, Write
---

# Work on GitHub Issue

Work on a GitHub issue following a systematic workflow that ensures proper branching,
task tracking, conventional commits, and clean git state.

## Usage

`/issue <issue-number>`

## General Rules

- Never make changes outside the current Git repository
- Use simple, explicit git and gh commands over complex scripting
- If any step fails, stop and clearly explain what happened
- Use ONLY these Conventional Commit types: `feat`, `fix`, `refactor`, `perf`, `chore`, `docs`, `ci`, `style`, `build`
- Commit messages must follow: `<type>(optional-scope): <short, imperative description>`
- Use TodoWrite to track all tasks throughout the workflow
- Wait for approval if the solution is not trivial or obvious

## Workflow

### Step 0: Fetch and Analyze Issue

1. Fetch issue details: `gh issue view <number>`
2. Auto-assign issue: `gh issue edit <number> --add-assignee @me`
3. Analyze the issue to understand:
   - What type of work is this? (feature, fix, refactor, etc.)
   - What is the scope?
   - What needs to be done?
4. Create initial TodoWrite task list based on issue analysis

### Step 1: Handle Dirty Working Directory

Check current git state:

- `git status` - check for staged, unstaged, and untracked changes

**If working directory is dirty:**

1. Get current branch: `git branch --show-current`
2. Stage all changes: `git add -A`
3. Commit with WIP message, skipping pre-commit (prek) hooks:
   `git commit -m "WIP: save progress before switching to issue <number>" --no-verify`
4. Verify clean state: `git status` should show clean working tree

**If working directory is clean:**

- Continue to next step

### Step 2: Create Issue Branch

1. Fetch latest: `git fetch origin`
2. Determine branch name from issue:
   - Format: `<type>/<number>-<short-description>`
   - Type based on issue analysis (feat, fix, refactor, etc.)
   - Description: kebab-case, 2-4 words max
   - Examples: `feat/344-add-auth`, `fix/342-oauth-bug`, `chore/100-update-deps`
3. Create and switch to new branch: `git switch -c <branch-name> origin/main`

### Step 3: Plan the Work

1. Update TodoWrite with detailed task breakdown for solving the issue
2. Assess complexity:
   - **Trivial/Obvious**: Clear bug fix, simple addition, obvious solution
   - **Non-trivial**: Requires design decisions, multiple approaches possible, significant changes

**If non-trivial:**

- Present the plan
- Wait for approval before proceeding
- Adjust plan based on feedback

**If trivial:**

- Proceed with implementation

### Step 4: Implement Solution

1. Work through tasks systematically, updating TodoWrite status as you go
2. Commit work in logical chunks following conventional commit format:
   - Each significant piece of functionality = separate commit
   - Each commit message: `<type>(optional-scope): <description>`
   - Never skip pre-commit (prek) hooks for implementation commits
3. Keep working tree clean between major steps
4. Update TodoWrite to mark tasks as in_progress/completed

### Step 5: Verify Completion

1. Run tests if applicable
2. Verify all TodoWrite tasks are completed
3. Ensure working tree is clean: `git status`
4. Review commits: `git log origin/main..HEAD`

### Step 6: Push and Create PR

1. Push branch: `git push -u origin <branch-name>`
2. Prepare PR details:
   - **Title**: Use conventional commit format matching the primary change
     - Single commit: use that commit message
     - Multiple commits: synthesize a clear title representing all changes
   - **Body**: Include:
     - Brief summary of changes (bullet points)
     - `Closes #<issue-number>` to auto-link the issue
     - Any testing or verification performed
3. Create PR:

   ```bash
   gh pr create --title "<conventional-commit-title>" \
     --body "<body-with-closes-statement>" \
     --base main --head <branch-name>
   ```

### Step 7: Final Output

Print:

- Issue number and title
- Branch name created
- Commit messages made
- PR URL
- TodoWrite task summary

If any step failed, clearly explain:

- What failed
- Which command failed
- What should be done manually to recover

## Important Constraints

- NEVER run destructive commands (`git reset --hard`, `git push --force`) without explicit instruction
- ALWAYS use conventional commit types: `feat`, `fix`, `refactor`, `perf`, `chore`, `docs`, `ci`, `style`, `build`
- ALWAYS skip pre-commit (prek) hooks ONLY for WIP commits using `--no-verify`
- NEVER skip pre-commit (prek) hooks for implementation commits
- ALWAYS wait for approval on non-trivial changes
- ALWAYS link PR to issue with "Closes #<number>"
- ALWAYS use TodoWrite to track work
