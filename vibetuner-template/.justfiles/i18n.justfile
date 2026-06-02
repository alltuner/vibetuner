# Complete i18n workflow: extract, update, and compile translations
[group('localization')]
i18n: extract-translations update-locale-files compile-locales
    @echo "✓ Complete i18n workflow finished"

# Extracts translations from source files
[group('localization')]
extract-translations:
    @uv run --frozen pybabel extract --no-wrap --add-location=file -F babel.cfg -o locales/messages.pot .

# Creates a new language file for localization
[group('localization')]
new-locale LANG:
    @uv run --frozen pybabel init --no-wrap -i locales/messages.pot -d locales -l {{ LANG }}

# Updates existing language files for localization
[group('localization')]
update-locale-files:
    @find locales -type f -path "*/LC_MESSAGES/messages.po" -exec sh -c 'echo " ↺ {}"; msguniq --no-wrap "{}" -o "{}"; msgmerge --no-wrap --add-location=file --no-fuzzy-matching --update --backup=none --previous "{}" locales/messages.pot' \;

# Compiles the language files into binary format
[group('localization')]
compile-locales:
    @uv run --frozen pybabel compile -d locales

# Report any fuzzy-marked entries across all catalogs (gettext ignores them at runtime)
[group('localization')]
i18n-fuzzy-audit:
    #!/usr/bin/env bash
    set -euo pipefail

    found=0
    for po in $(find locales -type f -path "*/LC_MESSAGES/messages.po"); do
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

# Dump untranslated strings per language to a given DEST directory
[group('localization')]
dump-untranslated DEST:
    #!/usr/bin/env bash

    mkdir -p {{ DEST }}

    for LANG_DIR in locales/??; do
        LANG=$(basename ${LANG_DIR} | cut -d/ -f1)
        msgattrib --untranslated ./locales/${LANG}/LC_MESSAGES/messages.po > "{{ DEST }}/untranslated_${LANG}.po"
    done
