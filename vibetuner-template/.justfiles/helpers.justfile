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

# Compute project variables from pyproject.toml and .copier-answers.yml.
# Runs a single Python process instead of 4 separate ones.
# Usage in recipes: eval "$(just _project-vars)"
[private]
_project-vars:
    #!/usr/bin/env bash
    uv run --frozen python << 'PYEOF'
    import tomllib, yaml, os
    answers = yaml.safe_load(open('.copier-answers.yml')) if os.path.exists('.copier-answers.yml') else {}
    print(f"VERSION={tomllib.load(open('pyproject.toml', 'rb'))['project']['version']}")
    print(f"PYTHON_VERSION={open('.python-version').read().strip()}")
    print(f"COMPOSE_PROJECT_NAME={answers.get('project_slug', 'scaffolding').strip()}")
    print(f"FQDN={answers.get('fqdn', '').strip()}")
    print(f"ENABLE_WATCHTOWER={str(answers.get('enable_watchtower', False)).lower()}")
    PYEOF
