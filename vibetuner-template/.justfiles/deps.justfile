# Install dependencies from lockfiles
[group('Dependencies')]
install-deps:
    @bun install
    @uv sync --all-extras