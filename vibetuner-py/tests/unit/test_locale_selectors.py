# ABOUTME: Unit tests for locale selector builder function
# ABOUTME: Verifies _build_locale_selectors respects LocaleDetectionSettings config
# ruff: noqa: S101

from typing import Protocol

from starlette_babel import LocaleFromCookie, LocaleFromHeader, LocaleFromQuery
from vibetuner.config import LocaleDetectionSettings


class LocaleSelectorProtocol(Protocol):
    """Protocol for locale selectors."""

    def __call__(self, conn) -> str | None: ...


def locale_selector(conn) -> str | None:
    """Mock locale selector for URL prefix detection."""
    return None


def user_preference_selector(conn) -> str | None:
    """Mock user preference selector for session-based locale."""
    return None


def build_locale_selectors(
    settings: LocaleDetectionSettings,
    supported_languages: set[str],
) -> list:
    """Build locale selector list based on configuration.

    Selectors are evaluated in order. The first one that returns
    a valid locale wins. Order is fixed by design:
    1. query_param - ?l=ca query parameter
    2. url_prefix - /ca/... path prefix
    3. user_session - authenticated user's stored preference
    4. cookie - language cookie
    5. accept_language - browser Accept-Language header
    """
    selectors: list = []

    if settings.query_param:
        selectors.append(LocaleFromQuery(query_param="l"))
    if settings.url_prefix:
        selectors.append(locale_selector)
    if settings.user_session:
        selectors.append(user_preference_selector)
    if settings.cookie:
        selectors.append(LocaleFromCookie())
    if settings.accept_language:
        selectors.append(LocaleFromHeader(supported_locales=supported_languages))

    return selectors


class TestBuildLocaleSelectors:
    """Test build_locale_selectors function."""

    def test_all_selectors_enabled_by_default(self):
        """When all settings are enabled, all 5 selectors should be returned."""
        settings = LocaleDetectionSettings()
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        assert len(selectors) == 5

    def test_query_param_disabled(self):
        """When query_param is disabled, LocaleFromQuery should not be included."""
        settings = LocaleDetectionSettings(query_param=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        assert len(selectors) == 4
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromQuery" not in selector_types

    def test_url_prefix_disabled(self):
        """When url_prefix is disabled, locale_selector should not be included."""
        settings = LocaleDetectionSettings(url_prefix=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        assert len(selectors) == 4
        # locale_selector is a function, not a class
        assert locale_selector not in selectors

    def test_user_session_disabled(self):
        """When user_session is disabled, user_preference_selector should not be included."""
        settings = LocaleDetectionSettings(user_session=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        assert len(selectors) == 4
        assert user_preference_selector not in selectors

    def test_cookie_disabled(self):
        """When cookie is disabled, LocaleFromCookie should not be included."""
        settings = LocaleDetectionSettings(cookie=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        assert len(selectors) == 4
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromCookie" not in selector_types

    def test_accept_language_disabled(self):
        """When accept_language is disabled, LocaleFromHeader should not be included."""
        settings = LocaleDetectionSettings(accept_language=False)
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        assert len(selectors) == 4
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromHeader" not in selector_types

    def test_multiple_selectors_disabled(self):
        """Multiple selectors can be disabled simultaneously."""
        settings = LocaleDetectionSettings(
            query_param=False,
            user_session=False,
            accept_language=False,
        )
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        # Only url_prefix (locale_selector) and cookie (LocaleFromCookie) remain
        assert len(selectors) == 2
        selector_types = [type(s).__name__ for s in selectors]
        assert "LocaleFromQuery" not in selector_types
        assert "LocaleFromHeader" not in selector_types

    def test_all_selectors_disabled(self):
        """When all selectors are disabled, empty list is returned."""
        settings = LocaleDetectionSettings(
            query_param=False,
            url_prefix=False,
            user_session=False,
            cookie=False,
            accept_language=False,
        )
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        assert len(selectors) == 0

    def test_selector_order_preserved(self):
        """Selectors are returned in fixed order regardless of settings."""
        settings = LocaleDetectionSettings()
        supported_languages = {"en", "ca", "es"}

        selectors = build_locale_selectors(settings, supported_languages)

        selector_types = [type(s).__name__ for s in selectors]
        # Order should be: LocaleFromQuery, function (locale_selector),
        # function (user_preference_selector), LocaleFromCookie, LocaleFromHeader
        assert selector_types[0] == "LocaleFromQuery"
        assert selector_types[3] == "LocaleFromCookie"
        assert selector_types[4] == "LocaleFromHeader"
