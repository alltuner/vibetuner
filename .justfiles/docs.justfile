
# Serve documentation locally with live reload
[group('Documentation')]
docs-serve:
    @cd vibetuner-docs && uvx --with mkdocs-material mkdocs serve

# Build documentation
[group('Documentation')]
docs-build:
    @cd vibetuner-docs && uvx --with mkdocs-material mkdocs build --site-dir ../_site

