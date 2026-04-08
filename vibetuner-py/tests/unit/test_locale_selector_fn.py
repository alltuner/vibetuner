# ABOUTME: Tests that locale_selector reads lang_prefix from scope state
# ABOUTME: Validates the fix for #1606 where LangPrefixMiddleware strips the path before locale detection
# ruff: noqa: S101

"""
Tests for locale_selector function.

Uses a local copy of locale_selector because importing vibetuner.frontend.middleware
triggers vibetuner.frontend.__init__.py which mounts static file directories that
don't exist in tests. This pattern matches test_locale_selectors.py.
"""

from starlette.requests import HTTPConnection


def locale_selector(conn: HTTPConnection) -> str | None:
    """Selects the locale from the language prefix extracted by LangPrefixMiddleware."""
    return conn.scope.get("state", {}).get("lang_prefix")


def _make_conn(path: str = "/", state: dict | None = None) -> HTTPConnection:
    """Create a minimal HTTPConnection with the given scope."""
    scope: dict = {"type": "http", "path": path}
    if state is not None:
        scope["state"] = state
    return HTTPConnection(scope)


class TestLocaleSelector:
    def test_returns_lang_prefix_from_state(self):
        """Should return the lang_prefix set by LangPrefixMiddleware."""
        conn = _make_conn(path="/dashboard", state={"lang_prefix": "ca"})
        assert locale_selector(conn) == "ca"

    def test_returns_none_without_lang_prefix(self):
        """Should return None when no lang prefix was detected."""
        conn = _make_conn(path="/dashboard", state={})
        assert locale_selector(conn) is None

    def test_returns_none_without_state(self):
        """Should return None when scope has no state dict."""
        conn = _make_conn(path="/dashboard")
        assert locale_selector(conn) is None

    def test_does_not_parse_path(self):
        """Should NOT detect language from the path itself (that's LangPrefixMiddleware's job)."""
        conn = _make_conn(path="/ca/dashboard", state={})
        assert locale_selector(conn) is None

    def test_works_after_prefix_stripped(self):
        """Simulates the real scenario: path is stripped but lang_prefix is in state."""
        # LangPrefixMiddleware strips /ca/dashboard -> /dashboard
        # and sets state["lang_prefix"] = "ca"
        conn = _make_conn(path="/dashboard", state={"lang_prefix": "ca"})
        assert locale_selector(conn) == "ca"
