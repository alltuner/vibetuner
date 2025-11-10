[group('Helpers')]
_check-clean:
    @git diff --quiet || (echo "❌ Uncommitted changes found. Commit or stash them before building." && exit 1)
    @git diff --cached --quiet || (echo "❌ Staged but uncommitted changes found. Commit them before building." && exit 1)

[group('Helpers')]
_check-unpushed-commits:
    @git fetch origin > /dev/null
    @commits=`git rev-list HEAD ^origin/HEAD --count`; \
    if [ "$commits" -ne 0 ]; then \
        echo "❌ You have local commits that haven't been pushed."; \
        exit 1; \
    fi

[group('Helpers')]
_check-last-commit-tagged:
    @if [ -z "$(git tag --points-at HEAD)" ]; then \
        echo "❌ Current commit is not tagged."; \
        echo "   Please checkout a clean tag before building production."; \
        exit 1; \
    fi