# Format Python files with ruff
[group('Code quality: formatting')]
format-py:
    @uv run ruff format .

# Format TOML files with taplo
[group('Code quality: formatting')]
format-toml:
    @uv run taplo fmt

# Format Jinja files with djlint
[group('Code quality: formatting')]
format-jinja:
    @uv run djlint . --reformat

# Format YAML files with dprint
[group('Code quality: formatting')]
format-yaml:
    @uvx --from dprint-py dprint fmt --plugins https://plugins.dprint.dev/g-plane/pretty_yaml-v0.5.1.wasm

# Format Markdown files with rumdl
[group('Code quality: formatting')]
format-md:
    @uv run rumdl fmt

# Format all code
[group('Code quality: formatting')]
format: format-py format-toml format-jinja format-md