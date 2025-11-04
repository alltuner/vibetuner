#!/bin/bash
# ABOUTME: Compares contents of two directories and categorizes files by presence and differences.
# ABOUTME: Reports files unique to each directory, identical in both, or different in both.

set -e

# Check arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <folder_a> <folder_b>"
    exit 1
fi

FOLDER_A="$1"
FOLDER_B="$2"

# Verify folders exist
if [ ! -d "$FOLDER_A" ]; then
    echo "Error: Directory '$FOLDER_A' does not exist"
    exit 1
fi

if [ ! -d "$FOLDER_B" ]; then
    echo "Error: Directory '$FOLDER_B' does not exist"
    exit 1
fi

# Arrays to store results
only_in_a=()
only_in_b=()
identical=()
different=()

# Get all files in both directories (relative paths)
files_a=$(cd "$FOLDER_A" && find . -type f | sed 's|^\./||' | sort)
files_b=$(cd "$FOLDER_B" && find . -type f | sed 's|^\./||' | sort)

# Create associative arrays (using temp files for portability)
temp_a=$(mktemp)
temp_b=$(mktemp)
echo "$files_a" > "$temp_a"
echo "$files_b" > "$temp_b"

# Process all unique file paths
all_files=$(cat "$temp_a" "$temp_b" | sort -u)

while IFS= read -r file; do
    [ -z "$file" ] && continue

    file_in_a=false
    file_in_b=false

    [ -f "$FOLDER_A/$file" ] && file_in_a=true
    [ -f "$FOLDER_B/$file" ] && file_in_b=true

    if $file_in_a && $file_in_b; then
        # File exists in both - compare contents
        if cmp -s "$FOLDER_A/$file" "$FOLDER_B/$file"; then
            identical+=("$file")
        else
            different+=("$file")
        fi
    elif $file_in_a; then
        only_in_a+=("$file")
    elif $file_in_b; then
        only_in_b+=("$file")
    fi
done <<< "$all_files"

# Clean up temp files
rm -f "$temp_a" "$temp_b"

# Display results
for file in "${identical[@]}"; do
    echo "✓ $file"
done

for file in "${different[@]}"; do
    echo "≠ $file"
done

for file in "${only_in_a[@]}"; do
    echo "A $file"
done

for file in "${only_in_b[@]}"; do
    echo "B $file"
done
