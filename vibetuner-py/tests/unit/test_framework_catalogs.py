# ABOUTME: Verifies the framework ships compiled .mo catalogs and that the
# ABOUTME: shared translator loads them so framework templates render localized
# ruff: noqa: S101

"""Tests that the framework's bundled translation catalogs ship and load.

The vibetuner package ships ``locales/<lang>/LC_MESSAGES/messages.mo`` so
consuming apps render framework templates in the active locale without
having to re-extract every core msgid into their own catalog. Without
these catalogs, every ``_()`` call in framework templates would fall
back to the English msgid even for non-English locales, which is what
issue #1858 reports.
"""

from starlette_babel import Translator, get_translator
from starlette_babel.translator import gettext
from vibetuner.paths import package_locales


def test_package_locales_directory_exists() -> None:
    """The framework must ship a locales directory with compiled .mo files."""
    assert package_locales is not None, (
        "vibetuner/locales/ is missing from the installed package — "
        "framework translations will silently fall back to English. "
        "Run `pybabel compile -d vibetuner-py/src/vibetuner/locales` to "
        "regenerate the .mo catalogs."
    )
    assert package_locales.is_dir()


def test_catalan_catalog_is_compiled() -> None:
    """Catalan messages.mo must be present so issue #1858 stays fixed."""
    assert package_locales is not None
    mo_path = package_locales / "ca" / "LC_MESSAGES" / "messages.mo"
    assert mo_path.is_file(), (
        f"Expected {mo_path} to exist. Run "
        "`pybabel compile -d vibetuner-py/src/vibetuner/locales` to "
        "regenerate it from messages.po."
    )


def test_english_catalog_is_compiled() -> None:
    """English messages.mo must be present (acts as the default catalog)."""
    assert package_locales is not None
    mo_path = package_locales / "en" / "LC_MESSAGES" / "messages.mo"
    assert mo_path.is_file()


def test_catalan_login_strings_translate() -> None:
    """The login page's user-facing strings must translate to Catalan.

    These are exactly the strings the issue reporter saw rendering in
    English when their app's active locale was ``ca``.
    """
    assert package_locales is not None
    translator = Translator([package_locales])

    # Strings called out in the issue body
    assert translator.gettext("Welcome Back", locale="ca") == (
        "Et donem la benvinguda de nou"
    )
    assert translator.gettext("Choose your preferred sign-in method", locale="ca") == (
        "Tria el teu mètode d'inici de sessió preferit"
    )
    assert translator.gettext("Send Magic Link", locale="ca") == "Envia l'enllaç màgic"
    assert translator.gettext("No password required!", locale="ca") == (
        "No cal contrasenya!"
    )
    assert translator.gettext(
        "We'll send you a secure link to sign in instantly.",
        locale="ca",
    ) == ("T'enviarem un enllaç segur per iniciar la sessió a l'instant.")
    assert translator.gettext("OR", locale="ca") == "O BÉ"
    # The one string that was previously translating "by accident" because
    # apps re-translate it for their own forms — must still translate now.
    assert translator.gettext("Email Address", locale="ca") == (
        "Adreça de correu electrònic"
    )


def test_missing_msgid_falls_back_to_msgid() -> None:
    """Unknown msgids return the msgid itself (gettext's NullTranslations behavior)."""
    assert package_locales is not None
    translator = Translator([package_locales])
    assert (
        translator.gettext("this msgid is not in any catalog", locale="ca")
        == "this msgid is not in any catalog"
    )


def test_shared_translator_loads_framework_catalogs_on_middleware_import() -> None:
    """Importing vibetuner.frontend.middleware loads the framework catalogs.

    The middleware module installs the framework's bundled catalogs into
    the process-global ``shared_translator`` at import time, so any code
    that later calls :func:`starlette_babel.gettext` (or evaluates a
    :class:`LazyString`) automatically picks them up — no per-app
    initialization required.
    """
    import vibetuner.frontend.middleware  # noqa: F401 - import triggers load

    translator = get_translator()
    # The shared translator should now know about Catalan framework strings
    assert (
        translator.gettext("Welcome Back", locale="ca")
        == "Et donem la benvinguda de nou"
    )


def test_app_catalog_overrides_framework_catalog(tmp_path) -> None:
    """Project catalogs loaded after the framework win on collision.

    starlette_babel's ``Translator.add_translations`` merges domains in
    load order. ``frontend/middleware.py`` loads the framework catalog
    first and the project catalog second, so an app that translates
    ``"Welcome Back"`` itself overrides the framework's translation.
    """
    # Build a fake project-side catalog with a single override.
    app_locales = tmp_path / "locales" / "ca" / "LC_MESSAGES"
    app_locales.mkdir(parents=True)

    po_source = (
        b'msgid ""\nmsgstr ""\n'
        b'"Content-Type: text/plain; charset=utf-8\\n"\n\n'
        b'msgid "Welcome Back"\n'
        b'msgstr "Hola de nou (app override)"\n'
    )
    po_path = app_locales / "messages.po"
    po_path.write_bytes(po_source)

    # Compile inline using msgfmt-equivalent (babel.messages.mofile).
    from babel.messages.mofile import write_mo
    from babel.messages.pofile import read_po

    with po_path.open("rb") as f:
        catalog = read_po(f, locale="ca", domain="messages")
    mo_path = app_locales / "messages.mo"
    with mo_path.open("wb") as f:
        write_mo(f, catalog)

    # Framework catalogs loaded first, app catalogs loaded second.
    translator = Translator()
    assert package_locales is not None
    translator.load_from_directories([package_locales])
    translator.load_from_directories([tmp_path / "locales"])

    assert (
        translator.gettext("Welcome Back", locale="ca") == "Hola de nou (app override)"
    )
    # Untouched framework strings still translate
    assert translator.gettext("Sign In", locale="ca") == "Inicia la sessió"


def test_module_level_gettext_uses_shared_translator() -> None:
    """Importing the middleware also wires up module-level gettext()."""
    import vibetuner.frontend.middleware  # noqa: F401

    assert gettext("Welcome Back", locale="ca") == "Et donem la benvinguda de nou"
