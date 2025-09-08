---
name: format
description: Format and lint all code (Python with ruff, templates with djlint)
allowed-tools: Bash(ruff:*), Bash(uv:*), Bash(djlint:*), Bash(markdownlint:*)
---

I'll format and lint all code in the project.

This command will:

1. 🐍 **Format Python code**: `ruff format .`
   - Formats all Python files according to project standards
   - Uses Black-compatible formatting

2. 🔍 **Lint Python code**: `ruff check --fix .`
   - Runs all linting rules and auto-fixes issues where possible
   - Includes import sorting, unused imports, etc.

3. 🎨 **Format HTML templates**: `djlint --reformat templates/`
   - Formats all .html.jinja template files in the templates directory
   - Uses djlint for consistent HTML/Jinja2 formatting

4. 📝 **Lint Markdown files**: `pnpm markdownlint **/*.md --fix`
   - Lints and auto-fixes markdown files
   - Ensures consistent markdown formatting and style

Let me run the formatting and linting:

!ruff format . && ruff check --fix . && djlint --reformat templates/ --quiet && pnpm markdownlint **/*.md --fix

This will:

- Format all Python code consistently
- Fix linting issues automatically where possible
- Format Jinja2 templates for better readability
- Install djlint if not available (using uv tool install)

**What gets formatted:**

- All `.py` files - consistent Python formatting
- All `.html.jinja` files - consistent HTML template formatting  
- All `.md` files - consistent markdown formatting
- Auto-fixes common linting issues (imports, unused variables, etc.)

**Safe to run:** Only makes formatting and style changes, doesn't modify logic.
