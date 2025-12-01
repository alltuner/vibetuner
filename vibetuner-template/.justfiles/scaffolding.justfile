import 'deps.justfile'

# Update to the latest version of the project scaffolding
[group('scaffolding')]
update-scaffolding:
    @echo "Updating project scaffolding..."
    @copier update -A --trust
    
    # Check package.json and conditionally install
    @if [ -f package.json ]; then \
        if grep -q "<<<<<<<\|=======\|>>>>>>>" package.json; then \
            echo "⚠️  Conflicts detected in package.json - skipping bun install"; \
            echo "Please resolve conflicts manually and run: bun install"; \
        else \
            echo "✅ No conflicts in package.json - running bun install"; \
            bun install; \
        fi \
    fi
    
    # Check pyproject.toml and conditionally sync
    @if [ -f pyproject.toml ]; then \
        if grep -q "<<<<<<<\|=======\|>>>>>>>" pyproject.toml; then \
            echo "⚠️  Conflicts detected in pyproject.toml - skipping uv sync"; \
            echo "Please resolve conflicts manually and run: uv sync --all-extras"; \
        else \
            echo "✅ No conflicts in pyproject.toml - running uv sync"; \
            uv sync --all-extras --no-sources; \
        fi \
    fi
    
    @echo "Project scaffolding update completed."
    @echo "Please review the changes and resolve any conflicts before committing."

# Initialize git repo
[group('initialization')]
git-init PROJECT: install-deps
    @[ -d .git ] || (git init && git add . && SKIP=no-commit-to-branch git commit -m "initial commit for {{ PROJECT }}" && git tag -a "v0.0.1" -m "Initial version")

[group('initialization')]
create-github-repo REPO:
    @gh repo create {{ REPO }} --private -s . --push
