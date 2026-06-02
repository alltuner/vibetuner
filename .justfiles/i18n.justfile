# Framework translation catalog management for vibetuner-py.
#
# The framework ships .mo catalogs under vibetuner-py/src/vibetuner/locales/
# so consuming apps render framework templates in their active locale
# without re-extracting every core msgid into their own catalog. These
# recipes regenerate the catalogs from source. .po and .mo files are
# committed to the repo — the recipes only run when a contributor edits
# a translatable string or adds a new locale.

# Full framework i18n workflow: extract, update existing .po files, compile
[group('localization')]
i18n-framework: extract-framework-translations update-framework-locales compile-framework-locales
    @echo "✓ Framework i18n workflow finished"

# Extract translatable strings from the framework into messages.pot
[group('localization')]
extract-framework-translations:
    @cd vibetuner-py && uv run --frozen pybabel extract \
        --no-wrap \
        --add-location=file \
        -F babel.cfg \
        --project=vibetuner \
        --copyright-holder="All Tuner Labs, S.L." \
        --msgid-bugs-address="https://github.com/alltuner/vibetuner/issues" \
        -o src/vibetuner/locales/messages.pot \
        .

# Create a new framework locale (e.g. `just new-framework-locale es`)
[group('localization')]
new-framework-locale LANG:
    @cd vibetuner-py && uv run --frozen pybabel init \
        --no-wrap \
        -i src/vibetuner/locales/messages.pot \
        -d src/vibetuner/locales \
        -l {{ LANG }}

# Merge messages.pot updates into existing framework .po files
[group('localization')]
update-framework-locales:
    @cd vibetuner-py && find src/vibetuner/locales -type f -path "*/LC_MESSAGES/messages.po" \
        -exec sh -c 'echo " ↺ {}"; msguniq --no-wrap "{}" -o "{}"; msgmerge --no-wrap --add-location=file --no-fuzzy-matching --update --backup=none --previous "{}" src/vibetuner/locales/messages.pot' \;

# Compile framework .po files to .mo files (the wheel ships .mo only)
[group('localization')]
compile-framework-locales:
    @cd vibetuner-py && uv run --frozen pybabel compile -d src/vibetuner/locales

# Report any fuzzy-marked entries across framework catalogs (gettext ignores them at runtime)
[group('localization')]
i18n-framework-fuzzy-audit:
    #!/usr/bin/env bash
    set -euo pipefail

    found=0
    for po in $(find vibetuner-py/src/vibetuner/locales -type f -path "*/LC_MESSAGES/messages.po"); do
        count=$(grep -c '^#, fuzzy' "${po}" || true)
        if [ "${count}" -gt 0 ]; then
            echo " ⚠ ${po}: ${count} fuzzy entr$([ "${count}" -eq 1 ] && echo y || echo ies)"
            found=$((found + count))
        fi
    done

    if [ "${found}" -eq 0 ]; then
        echo "✓ No fuzzy entries found"
    else
        echo "Found ${found} fuzzy entr$([ "${found}" -eq 1 ] && echo y || echo ies); review the listed catalogs."
        exit 1
    fi
