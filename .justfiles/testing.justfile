# Run all tests
[group('Testing')]
test:
    @echo "🧪 Running all tests..."
    @cd vibetuner-py && uv run --frozen --extra test pytest
    @echo "✅ All tests passed"

# Run tests with verbose output
[group('Testing')]
test-verbose:
    @echo "🧪 Running all tests (verbose)..."
    @cd vibetuner-py && uv run --frozen --extra test pytest -v
    @echo "✅ All tests passed"

# Run only unit tests
[group('Testing')]
test-unit:
    @echo "🧪 Running unit tests..."
    @cd vibetuner-py && uv run --frozen --extra test pytest tests/unit/ -v
    @echo "✅ Unit tests passed"

# Run a specific test file
[group('Testing')]
test-file FILE:
    @echo "🧪 Running tests in {{FILE}}..."
    @cd vibetuner-py && uv run --frozen --extra test pytest {{FILE}} -v

# Run tests matching a keyword expression
[group('Testing')]
test-match KEYWORD:
    @echo "🧪 Running tests matching '{{KEYWORD}}'..."
    @cd vibetuner-py && uv run --frozen --extra test pytest -k "{{KEYWORD}}" -v
