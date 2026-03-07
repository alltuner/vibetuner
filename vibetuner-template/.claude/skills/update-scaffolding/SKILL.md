---
name: update-scaffolding
description: "Update project scaffolding to the latest vibetuner template version. Checks for updates, applies them in an isolated worktree, resolves conflicts, updates dependencies, and creates a PR. Triggers on: update scaffolding, upgrade vibetuner, sync template, update template, scaffolding update."
---

# Update Scaffolding Skill

Updates this project's scaffolding to the latest vibetuner template version,
resolves conflicts, updates dependencies, and creates a PR.

---

## Step 1: Check for Updates

Before doing any work, check if there is actually a newer version available.

Read `.copier-answers.yml` in the project root to find the current template
commit. Then check the upstream repository for newer commits:

```bash
# Get the current commit from copier answers
current_commit=$(grep '_commit:' .copier-answers.yml | awk '{print $2}')
template_url=$(grep '_src_path:' .copier-answers.yml | awk '{print $2}')

# Check latest commit on the template repo's default branch
latest_commit=$(git ls-remote "$template_url" HEAD | awk '{print $1}')

echo "Current: $current_commit"
echo "Latest:  $latest_commit"
```

If the commits match, inform the user that the scaffolding is already
up to date and stop. Do NOT proceed with the update.

If you cannot determine the upstream state (e.g., private repo, no network),
warn the user and ask whether to proceed anyway.

---

## Step 2: Run the Update in an Isolated Worktree

Use the **Agent tool** with `isolation: "worktree"` to perform all work in an
isolated copy of the repository. This prevents interference with the user's
working tree.

Give the worktree agent the following instructions:

### 2a. Update Dependencies

```bash
just update-and-commit-repo-deps
```

If there are no dependency changes, that is fine - continue to the next step.

### 2b. Update Scaffolding

```bash
just update-scaffolding
```

This runs `uvx copier update -A --trust` and attempts to install dependencies.

### 2c. Detect and Resolve Conflicts

After the scaffolding update, check ALL files for merge conflict markers:

```bash
grep -rn '<<<<<<<\|=======\|>>>>>>>' --include='*.py' --include='*.toml' \
  --include='*.json' --include='*.yml' --include='*.yaml' --include='*.md' \
  --include='*.html' --include='*.html.jinja' --include='*.css' --include='*.js' \
  --include='*.just' --include='*.justfile' --include='Dockerfile' \
  --include='*.cfg' --include='*.txt' . || echo "No conflicts found"
```

For each conflicted file:

1. **Read the file** to understand both sides of the conflict
2. **Resolve intelligently:**
   - For `package.json` / `pyproject.toml` / lock files: keep the newer
     upstream versions of dependencies, preserve any project-specific additions
   - For config files (`.yml`, `.toml`, `.cfg`): prefer upstream values for
     framework settings, keep project-specific customizations
   - For templates (`.html.jinja`): prefer upstream structure, preserve
     project-specific content blocks
   - For source code in `src/app/`: prefer the project's version (user code
     takes precedence over template defaults)
   - For justfiles, CI workflows, Dockerfiles: prefer upstream (infrastructure
     should stay current)
3. **If a conflict cannot be resolved with confidence**, leave the conflict
   markers in place and note the file path - these will be flagged in the PR

### 2d. Install Dependencies (if not already done)

After resolving conflicts, ensure dependencies are synced:

```bash
bun install
uv sync --all-extras
```

### 2e. Commit All Changes

```bash
git add -A
git commit -m "chore: update scaffolding to latest vibetuner template"
```

### 2f. Push and Create PR

```bash
git push -u origin "$(git branch --show-current)"
```

Then create a PR using `gh pr create`:

- **Title:** `chore: update scaffolding to latest vibetuner template`
- **Body:** Include:
  - Summary of what was updated (dependencies, template files)
  - List of files that had conflicts and how they were resolved
  - If any conflicts could NOT be resolved: clearly list them with
    instructions for manual resolution
  - A note that the PR should be reviewed before merging

**If there are unresolved conflicts**, add a PR comment explaining which files
need manual attention and do NOT merge the PR. Inform the user.

**If everything resolved cleanly**, inform the user that the PR is ready for
review and can be merged.

---

## Important Notes

- NEVER force-push or modify the main branch directly
- ALWAYS create a PR for review, even if everything resolved cleanly
- The PR title MUST use conventional commit format (`chore:` prefix)
- If `just` commands fail, diagnose the issue - don't retry blindly
- Report the PR URL back to the user when done
