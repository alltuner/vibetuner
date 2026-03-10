# ABOUTME: Justfile recipes for running tests.
# ABOUTME: Provides test and test-v commands using pytest via uv.

# Run all tests
[group('Testing')]
test *ARGS:
    @uv run --frozen pytest {{ ARGS }}

# Run tests with verbose output
[group('Testing')]
test-v *ARGS:
    @uv run --frozen pytest -v {{ ARGS }}
