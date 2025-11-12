# Format Python files with ruff
[group('formatting')]
format-py:
    @uv run ruff format .

# Format TOML files with taplo
[group('formatting')]
format-toml:
    @uv run taplo fmt

[group('formatting')]
format-jinja:
    @uv run djlint . --reformat


# Format all code
[group('formatting')]
format: format-py format-toml format-jinja