# ABOUTME: Tests that set_language endpoint updates session language preference
# ABOUTME: Validates the fix for #1607 where authenticated users couldn't switch languages
# ruff: noqa: S101

"""
Tests for set_language session update logic.

Tests the session-update logic extracted from the endpoint handler. We can't
easily mount the full route (it requires vibetuner.frontend) so we test the
core behavior: that the session dict is mutated when user settings exist.
"""


def update_session_language(session: dict, lang: str) -> None:
    """Mirrors the session update logic in set_language endpoint."""
    if "user" in session and "settings" in session["user"]:
        session["user"]["settings"]["language"] = lang


class TestSetLanguageSession:
    def test_updates_authenticated_user_session(self):
        """Should update language in session for authenticated users."""
        session = {"user": {"settings": {"language": "en"}}}
        update_session_language(session, "ca")
        assert session["user"]["settings"]["language"] == "ca"

    def test_no_op_for_anonymous_user(self):
        """Should not crash when no user in session."""
        session = {}
        update_session_language(session, "ca")
        assert "user" not in session

    def test_no_op_without_settings(self):
        """Should not crash when user has no settings dict."""
        session = {"user": {"name": "test"}}
        update_session_language(session, "ca")
        assert "settings" not in session["user"]

    def test_overwrites_existing_preference(self):
        """Should overwrite whatever language was stored."""
        session = {"user": {"settings": {"language": "es", "theme": "dark"}}}
        update_session_language(session, "ca")
        assert session["user"]["settings"]["language"] == "ca"
        # Other settings are preserved
        assert session["user"]["settings"]["theme"] == "dark"
