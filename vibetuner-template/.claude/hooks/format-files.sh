#!/bin/bash
set -e

# Get the list of files that were modified by the Write/Edit/MultiEdit operation
# The CLAUDE_EDITED_FILES environment variable contains the file paths
if [ -z "$CLAUDE_EDITED_FILES" ]; then
    exit 0
fi

# Convert the file list to an array
IFS=$'\n' read -d '' -r -a files <<< "$CLAUDE_EDITED_FILES" || true

# Flag to track if any files were formatted
formatted=false

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        case "$file" in
            *.py)
                echo "🐍 Formatting Python: $file"
                ruff format "$file" 2>/dev/null || true
                ruff check --fix "$file" 2>/dev/null || true
                formatted=true
                ;;
            *.md)
                echo "📝 Formatting Markdown: $file"
                bun markdownlint --fix "$file" 2>/dev/null || true
                formatted=true
                ;;
            *.html.jinja)
                echo "🎨 Formatting HTML Template: $file"
                djlint --reformat "$file" --quiet 2>/dev/null || true
                formatted=true
                ;;
        esac
    fi
done

if [ "$formatted" = true ]; then
    echo "✨ Auto-formatting completed"
fi