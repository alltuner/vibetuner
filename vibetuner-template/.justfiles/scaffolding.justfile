import 'deps.justfile'

# Update to the latest version of the project scaffolding
[group('scaffolding')]
update-scaffolding:
    @echo "Updating project scaffolding..."
    @copier update -A --trust
    @bun install
    @uv sync --all-extras
    @echo "Project scaffolding updated."
    @echo "Please review the changes and commit."

# Initialize git repo
[group('initialization')]
git-init PROJECT: install-deps
    @[ -d .git ] || (git init && git add . && SKIP=no-commit-to-branch git commit -m "initial commit for {{ PROJECT }}" && git tag -a "v0.0.1" -m "Initial version")

[group('initialization')]
create-github-repo REPO:
    @gh repo create {{ REPO }} --private -s . --push
