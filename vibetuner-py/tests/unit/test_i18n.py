# ABOUTME: Unit tests for vibetuner.i18n public primitives
# ABOUTME: Covers register_locale_resolver, set_request_language, language_picker
# ruff: noqa: S101

"""Tests for the public i18n primitives.

The module under test is :mod:`vibetuner.i18n`. These tests exercise the
public surface only — internal registries are reset between tests via the
``reset_locale_resolvers`` fixture so registrations from one test do not
bleed into the next.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from babel import Locale
from starlette_babel import set_locale
from vibetuner import i18n


@pytest.fixture(autouse=True)
def reset_locale_resolvers():
    """Clear the resolver registry between tests."""
    i18n._reset_locale_resolvers()
    yield
    i18n._reset_locale_resolvers()


def _fake_request(language: str | None = None) -> MagicMock:
    """Build a minimal Request stand-in that supports request.state.language."""
    request = MagicMock()
    request.state = SimpleNamespace()
    if language is not None:
        request.state.language = language
    return request


def _fake_connection(state: dict | None = None) -> MagicMock:
    """Build a minimal HTTPConnection stand-in for selector calls."""
    conn = MagicMock()
    conn.scope = {"state": state or {}}
    return conn


class TestRegisterLocaleResolver:
    def test_resolver_appears_in_chain(self):
        def resolver(conn):
            return "ca"

        i18n.register_locale_resolver(resolver)
        chain = i18n.get_locale_resolvers()

        assert resolver in chain

    def test_resolvers_ordered_by_priority_low_first(self):
        first = MagicMock(return_value=None)
        second = MagicMock(return_value=None)
        third = MagicMock(return_value=None)

        i18n.register_locale_resolver(second, priority=10)
        i18n.register_locale_resolver(third, priority=20)
        i18n.register_locale_resolver(first, priority=0)

        chain = i18n.get_locale_resolvers()
        assert chain == [first, second, third]

    def test_combined_selector_returns_first_non_none(self):
        i18n.register_locale_resolver(lambda conn: None, priority=0)
        i18n.register_locale_resolver(lambda conn: "es", priority=10)
        i18n.register_locale_resolver(lambda conn: "ca", priority=20)

        combined = i18n.combined_locale_selector
        assert combined(_fake_connection()) == "es"

    def test_combined_selector_returns_none_when_all_none(self):
        i18n.register_locale_resolver(lambda conn: None)
        i18n.register_locale_resolver(lambda conn: None)

        assert i18n.combined_locale_selector(_fake_connection()) is None

    def test_combined_selector_with_no_resolvers_returns_none(self):
        assert i18n.combined_locale_selector(_fake_connection()) is None

    def test_combined_selector_swallows_resolver_exceptions(self, log_sink):
        def boom(conn):
            raise RuntimeError("kaboom")

        i18n.register_locale_resolver(boom, priority=0)
        i18n.register_locale_resolver(lambda conn: "ca", priority=10)

        assert i18n.combined_locale_selector(_fake_connection()) == "ca"
        assert any("kaboom" in m for m in log_sink)

    def test_register_rejects_non_callable(self):
        with pytest.raises(TypeError):
            i18n.register_locale_resolver("not a function")  # type: ignore[arg-type]


class TestSetRequestLanguage:
    def test_updates_request_state_and_babel_contextvar(self):
        request = _fake_request(language="en")
        # seed Babel context with a different language
        set_locale(Locale.parse("en"))

        i18n.set_request_language(request, "ca")

        assert request.state.language == "ca"
        from starlette_babel import get_locale

        assert str(get_locale()) == "ca"

    def test_rejects_non_string_code(self):
        request = _fake_request()
        with pytest.raises(TypeError):
            i18n.set_request_language(request, 42)  # type: ignore[arg-type]

    def test_rejects_invalid_locale_code(self):
        request = _fake_request()
        with pytest.raises(ValueError):
            i18n.set_request_language(request, "not-a-locale")

    def test_normalizes_to_lowercase(self):
        request = _fake_request()
        i18n.set_request_language(request, "CA")
        assert request.state.language == "ca"


class TestLanguagePicker:
    def test_returns_code_and_name_for_each_supported_language(self):
        result = i18n.language_picker(
            display_locale="en", supported_languages={"en", "ca", "es"}
        )

        codes = {entry["code"] for entry in result}
        assert codes == {"en", "ca", "es"}
        for entry in result:
            assert "code" in entry
            assert "name" in entry
            assert entry["name"]

    def test_names_render_in_requested_display_locale(self):
        en = i18n.language_picker(display_locale="en", supported_languages={"en", "es"})
        es = i18n.language_picker(display_locale="es", supported_languages={"en", "es"})

        en_map = {e["code"]: e["name"] for e in en}
        es_map = {e["code"]: e["name"] for e in es}

        assert en_map["es"].lower().startswith("spanish")
        assert es_map["es"].lower().startswith("español")
        assert es_map["en"].lower().startswith("inglés")

    def test_default_display_locale_uses_babel_contextvar(self):
        set_locale(Locale.parse("ca"))

        result = i18n.language_picker(supported_languages={"en", "ca", "es"})
        names = {e["code"]: e["name"] for e in result}

        assert names["es"].lower().startswith("espanyol")
        assert names["en"].lower().startswith("anglès")

    def test_result_is_sorted_by_name(self):
        result = i18n.language_picker(
            display_locale="en", supported_languages={"en", "ca", "es"}
        )
        names = [e["name"] for e in result]
        assert names == sorted(names)

    def test_supported_languages_defaults_to_settings(self):
        # No explicit list — should fall back to ctx.supported_languages.
        result = i18n.language_picker(display_locale="en")
        assert isinstance(result, list)
        assert all("code" in e and "name" in e for e in result)

    def test_exposed_as_jinja_global(self):
        from vibetuner.rendering import jinja_env

        assert jinja_env.globals.get("language_picker") is i18n.language_picker
