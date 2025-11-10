# Update root scaffolding deps
[group('Dependencies')]
update-repo-deps:
    @uvx uv-bump
    @uv lock --upgrade
    @uv sync --all-extras
    @bun update

# Update all dependencies and commit changes
[group('Dependencies')]
update-and-commit-repo-deps: update-repo-deps
    @git add pyproject.toml uv.lock bun.lock package.json
    @git commit -m "chore: update dependencies"

# Install dependencies from lockfiles
[group('Dependencies')]
install-deps:
    @bun install
    @uv sync --all-extras