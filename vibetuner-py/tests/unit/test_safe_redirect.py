# ABOUTME: Tests for the is_safe_redirect helper guarding post-auth redirect targets.
# ABOUTME: Rejects absolute URLs and protocol-relative paths to prevent open redirects.
# ruff: noqa: S101

from vibetuner.frontend.routes import is_safe_redirect


class TestIsSafeRedirect:
    """is_safe_redirect only accepts single-leading-slash relative paths."""

    def test_accepts_relative_path(self):
        assert is_safe_redirect("/dashboard") is True

    def test_accepts_relative_path_with_query(self):
        assert is_safe_redirect("/dashboard?tab=1") is True

    def test_accepts_relative_path_with_lang_prefix(self):
        assert is_safe_redirect("/en/dashboard") is True

    def test_rejects_absolute_https_url(self):
        assert is_safe_redirect("https://evil.com") is False

    def test_rejects_absolute_http_url(self):
        assert is_safe_redirect("http://evil.com/path") is False

    def test_rejects_protocol_relative_url(self):
        assert is_safe_redirect("//evil.com") is False

    def test_rejects_protocol_relative_url_with_path(self):
        assert is_safe_redirect("//evil.com/path") is False

    def test_rejects_path_without_leading_slash(self):
        assert is_safe_redirect("dashboard") is False

    def test_rejects_scheme_relative_backslash(self):
        # Browsers may treat backslashes as slashes; reject defensively.
        assert is_safe_redirect("/\\evil.com") is False
        assert is_safe_redirect("\\\\evil.com") is False

    def test_rejects_empty(self):
        assert is_safe_redirect("") is False

    def test_rejects_none(self):
        assert is_safe_redirect(None) is False

    def test_rejects_url_with_scheme_and_no_netloc(self):
        assert is_safe_redirect("javascript:alert(1)") is False
