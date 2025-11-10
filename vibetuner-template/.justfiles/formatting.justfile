# Format Python files with ruff
[group('formatting')]
format-py:
    uv run ruff format .

# Format TOML files with taplo
[group('formatting')]
format-toml:
    taplo fmt

# Format all code
[group('formatting')]
format: format-py format-toml