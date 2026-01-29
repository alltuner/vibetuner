# ABOUTME: Unit tests for locale selector builder logic
# ABOUTME: Verifies selector list is built correctly based on LocaleDetectionSettings
# ruff: noqa: S101

"""
Tests for the locale selector builder function.

NOTE: This test file contains a copy of the _build_locale_selectors logic rather
than importing from vibetuner.frontend.middleware. This is intentional because:

1. Importing vibetuner.frontend.middleware triggers vibetuner.frontend.__init__.py
2. The __init__ tries to mount static file directories that don't exist in tests
3. This causes RuntimeError before any mocking can take effect

This pattern matches test_lang_prefix_middleware.py which copies LangPrefixMiddleware
for the same reason. The test validates the logic; integration tests verify the
actual middleware configuration.
"""

from starlette_babel import LocaleFromCookie, LocaleFromHeader, LocaleFromQuery
from vibetuner.config import LocaleDetectionSettings


def locale_selector(conn) -> str | None:
    """Stub for URL prefix locale selector."""
    return None


def user_preference_selector(conn) -> str | None:
    """Stub for user session locale selector."""
    return None


def build_locale_selectors(
    config: LocaleDetectionSettings,
    supported_languages: set[str],
) -> list:
    """Build locale selector list based on configuration.

    Mirrors vibetuner.frontend.middleware._build_locale_selectors.

    Selectors are evaluated in order. The first one that returns
    a valid locale wins. Order is fixed by design:
    1. query_param - ?l=ca query parameter
    2. url_prefix - /ca/... path prefix
    3. user_session - authenticated user's stored preference
    4. cookie - language cookie
    5. accept_language - browser Accept-Language header
    """
    selectors: list = []

    if config.query_param:
        selectors.append(LocaleFromQuery(query_param="l"))
    if config.url_prefix:
        selectors.append(locale_selector)
    if config.user_session:
        selectors.append(user_preference_selector)
    if config.cookie:
        selectors.append(LocaleFromCookie())
    if config.accept_language:
        selectors.append(LocaleFromHeader(supported_locales=supported_languages))

    return selectors


class TestBuildLocaleSelectors:
    """Test build_locale_selectors function."""

    def test_all_selectors_enabled_by_default(self):
        """When all settings are enabled, all 5 selectors should be returned."""
        config = LocaleDetectionSettings()
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        assert len(selectors) == 5

    def test_query_param_disabled(self):
        """When query_param is disabled, LocaleFromQuery should not be included."""
        config = LocaleDetectionSettings(query_param=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        assert len(selectors) == 4
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromQuery" not in selector_types

    def test_url_prefix_disabled(self):
        """When url_prefix is disabled, locale_selector should not be included."""
        config = LocaleDetectionSettings(url_prefix=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        assert len(selectors) == 4
        assert locale_selector not in selectors

    def test_user_session_disabled(self):
        """When user_session is disabled, user_preference_selector not included."""
        config = LocaleDetectionSettings(user_session=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        assert len(selectors) == 4
        assert user_preference_selector not in selectors

    def test_cookie_disabled(self):
        """When cookie is disabled, LocaleFromCookie should not be included."""
        config = LocaleDetectionSettings(cookie=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        assert len(selectors) == 4
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromCookie" not in selector_types

    def test_accept_language_disabled(self):
        """When accept_language is disabled, LocaleFromHeader not included."""
        config = LocaleDetectionSettings(accept_language=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        assert len(selectors) == 4
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromHeader" not in selector_types

    def test_multiple_selectors_disabled(self):
        """Multiple selectors can be disabled simultaneously."""
        config = LocaleDetectionSettings(
            query_param=False,
            user_session=False,
            accept_language=False,
        )
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        # Only url_prefix (locale_selector) and cookie (LocaleFromCookie) remain
        assert len(selectors) == 2
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromQuery" not in selector_types
        assert "LocaleFromHeader" not in selector_types

    def test_all_selectors_disabled(self):
        """When all selectors are disabled, empty list is returned."""
        config = LocaleDetectionSettings(
            query_param=False,
            url_prefix=False,
            user_session=False,
            cookie=False,
            accept_language=False,
        )
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        assert len(selectors) == 0

    def test_selector_order_preserved(self):
        """Selectors are returned in fixed order regardless of settings."""
        config = LocaleDetectionSettings()
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(config, supported_languages)

        selector_types = [type(s).__name__ for s in selectors]
        # Order: LocaleFromQuery, function, function, LocaleFromCookie, LocaleFromHeader
        assert selector_types[0] == "LocaleFromQuery"
        assert selector_types[3] == "LocaleFromCookie"
        assert selector_types[4] == "LocaleFromHeader"
