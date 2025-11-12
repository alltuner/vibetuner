# Format Python files with ruff
[group('formatting')]
format-py:
    @uv run ruff format .

# Format TOML files with taplo
[group('formatting')]
format-toml:
    @uv run taplo fmt

# Format Jinja files with djlint
[group('formatting')]
format-jinja:
    @uv run djlint . --reformat

# Format YAML files with dprint
[group('formatting')]
format-yaml:
    @uvx --from dprint-py dprint fmt --plugins https://plugins.dprint.dev/g-plane/pretty_yaml-v0.5.1.wasm

# Format all code
[group('formatting')]
format: format-py format-toml format-jinja