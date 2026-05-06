
# Sync vibetuner core jinja templates into vibetuner-jinja so the
# npm package mirrors the canonical copy in vibetuner-py. Idempotent:
# skips if the destination is already up-to-date with the source. The
# same script runs as the package's npm `prepare` lifecycle hook, so
# `bun install` at the workspace root keeps things in sync automatically.
[group('Dependencies')]
sync-jinja:
    @bash vibetuner-jinja/scripts/sync.sh

# Update JavaScript dependencies in vibetuner-js
[group('Dependencies')]
update-js:
    @cd vibetuner-js && bun update

# Update Python dependencies in vibetuner-py
[group('Dependencies')]
update-py:
    @cd vibetuner-py && uvx uv-bump && uv lock --upgrade && uv sync --all-extras

# Update dependencies in vibetuner-template
[group('Dependencies')]
update-template:
    @cd vibetuner-template && bun update

# Update root scaffolding deps
[group('Dependencies')]
update-root:
    @uvx uv-bump && uv lock --upgrade && uv sync --all-extras

# Update all package dependencies
[group('Dependencies')]
update-all: update-js update-py update-template update-root

# Update all dependencies and commit changes
[group('Dependencies')]
update-and-commit: update-all update-precommit
    @git add pyproject.toml uv.lock \
        vibetuner-js/package.json vibetuner-js/bun.lock \
        vibetuner-py/pyproject.toml vibetuner-py/uv.lock \
        vibetuner-template/package.json

    @git commit -m "chore: update dependencies" \
        pyproject.toml uv.lock \
        vibetuner-js/package.json vibetuner-js/bun.lock \
        vibetuner-py/pyproject.toml vibetuner-py/uv.lock \
        vibetuner-template/package.json \
        || echo "No changes to commit"

# Update pre-commit hooks and commit changes
[group('Dependencies')]
update-precommit:
    @uv run --frozen prek auto-update
    @git add vibetuner-template/.pre-commit-config.yaml
    @git commit -m "chore: update pre-commit hooks" \
        vibetuner-template/.pre-commit-config.yaml \
        || echo "No pre-commit changes to commit"

# Full dependency update cycle: update deps, pre-commit, create PR, merge
[group('Dependencies')]
deps-pr:
    #!/usr/bin/env bash
    set -euo pipefail

    # Capture the repo root before any cd. The cleanup trap needs a git
    # repo in cwd to invoke `git worktree remove`; cd-ing to / (as we did
    # previously) put the trap outside any repo and it bailed with exit
    # 128 on every run, leaving worktrees and local branches behind.
    REPO_ROOT=$(git rev-parse --show-toplevel)
    DATE_STAMP=$(date +%Y-%m-%d)
    BRANCH="chore/update-deps-${DATE_STAMP}-$(date +%H%M)"
    WORKTREE_DIR=$(mktemp -d)

    cleanup() {
        cd "$REPO_ROOT"
        git worktree remove --force "$WORKTREE_DIR" || true
        git branch -D "$BRANCH" 2>/dev/null || true
    }
    trap cleanup EXIT

    git fetch origin main
    git worktree add -b "$BRANCH" "$WORKTREE_DIR" origin/main

    cd "$WORKTREE_DIR"

    just update-and-commit

    if [ "$(git rev-list origin/main..HEAD --count)" -eq 0 ]; then
        echo "All dependencies already up to date"
        exit 0
    fi

    # Build a self-documenting PR body: the commit subjects produced by
    # update-and-commit (one for prek auto-update, one for the actual
    # dependency bumps) plus a diffstat against main so reviewers can see
    # at a glance which lockfiles / manifests moved.
    PR_BODY=$(printf "## Updated\n\n%s\n\n## Files\n\n\`\`\`\n%s\n\`\`\`\n" \
        "$(git log --reverse --pretty=format:'- %s' "origin/main..HEAD")" \
        "$(git diff --stat "origin/main..HEAD")")

    git push -u origin "$BRANCH"
    gh pr create --title "chore: update deps ${DATE_STAMP}" --body "$PR_BODY" --base main
    # --auto queues the squash-merge for when required checks pass. Today
    # nothing required-blocks merge so this returns immediately, but it
    # makes the recipe robust against future branch protection rules.
    gh pr merge --auto --squash --subject "chore: update deps ${DATE_STAMP}"
    # Remote branch deletion is handled by GitHub's auto-delete-on-merge
    # setting; if it's off this is the fallback. Failure is fine — the
    # branch may already be gone or the merge may not have completed yet
    # (under --auto we return before merge lands).
    git push origin --delete "$BRANCH" 2>/dev/null || true
