
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
    @cd vibetuner-template && uvx uv-bump && uv lock --upgrade && uv sync --all-extras && bun update

# Update root scaffolding deps
[group('Dependencies')]
update-root:
    @uvx uv-bump && uv lock --upgrade && uv sync --all-extras

# Update all package dependencies
[group('Dependencies')]
update-all: update-js update-py update-template update-root

# Update all dependencies and commit changes
[group('Dependencies')]
update-and-commit: update-all
    @git add pyproject.toml uv.lock \
        vibetuner-js/package.json vibetuner-js/bun.lock \
        vibetuner-py/pyproject.toml vibetuner-py/uv.lock \
        vibetuner-template/pyproject.toml vibetuner-template/package.json

    @git commit -m "chore: update dependencies" \
        pyproject.toml uv.lock \
        vibetuner-js/package.json vibetuner-js/bun.lock \
        vibetuner-py/pyproject.toml vibetuner-py/uv.lock \
        vibetuner-template/pyproject.toml vibetuner-template/package.json \
        || echo "No changes to commit"
