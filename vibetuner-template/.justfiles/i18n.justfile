# Complete i18n workflow: extract, update, and compile translations
[group('localization')]
i18n: extract-translations update-locale-files compile-locales
    @echo "✓ Complete i18n workflow finished"

# Extracts translations from source files
[group('localization')]
extract-translations:
    @uv run --frozen pybabel extract -F babel.cfg -o locales/messages.pot .

# Creates a new language file for localization
[group('localization')]
new-locale LANG:
    @uv run --frozen pybabel init -i locales/messages.pot -d locales -l {{ LANG }}

# Updates existing language files for localization
[group('localization')]
update-locale-files:
    @find locales -type f -path "*/LC_MESSAGES/messages.po" -exec sh -c 'echo " ↺ {}"; msguniq "{}" -o "{}"; msgmerge --update --backup=none --previous "{}" locales/messages.pot' \;

# Compiles the language files into binary format
[group('localization')]
compile-locales:
    @uv run --frozen pybabel compile -d locales

# Dump untranslated strings per language to a given DEST directory
[group('localization')]
dump-untranslated DEST:
    #!/usr/bin/env bash

    mkdir -p {{ DEST }}

    for LANG_DIR in locales/??; do
        LANG=$(basename ${LANG_DIR} | cut -d/ -f1)
        msgattrib --untranslated ./locales/${LANG}/LC_MESSAGES/messages.po > "{{ DEST }}/untranslated_${LANG}.po"
    done
