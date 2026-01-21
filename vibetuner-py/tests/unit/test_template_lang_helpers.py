# ABOUTME: Unit tests for language-aware template helper functions
# ABOUTME: Verifies lang_url_for and hreflang_tags generate correct output for SEO
# ruff: noqa: S101

from unittest.mock import MagicMock


def lang_url_for(request, name: str, **path_params) -> str:
    """Test copy of helper to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.templates.lang_url_for.
    """
    base_url = request.url_for(name, **path_params).path
    lang = request.state.language
    return f"/{lang}{base_url}"


def hreflang_tags(request, supported_languages: set[str], default_lang: str) -> str:
    """Test copy of helper to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.templates.hreflang_tags.
    """
    path = request.url.path

    # If accessed with lang prefix, get the base path
    if hasattr(request.state, "lang_prefix"):
        path = request.state.original_path
        # Remove the language prefix to get base path
        parts = path.strip("/").split("/", 1)
        if parts and len(parts[0]) == 2:
            path = "/" + parts[1] if len(parts) > 1 else "/"

    base_url = str(request.base_url).rstrip("/")

    tags = []
    for lang in sorted(supported_languages):
        url = f"{base_url}/{lang}{path}"
        tags.append(f'<link rel="alternate" hreflang="{lang}" href="{url}" />')

    # x-default points to UNPREFIXED URL (not default language prefixed)
    default_url = f"{base_url}{path}"
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{default_url}" />')

    return "\n".join(tags)


def url_for_language(request, lang: str, name: str, **path_params) -> str:
    """Test copy of helper to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.templates.url_for_language.
    """
    base_url = request.url_for(name, **path_params).path
    return f"/{lang}{base_url}"


class TestUrlForLanguage:
    """Test url_for_language template helper."""

    def _mock_request(self, url_for_result: str = "/dashboard"):
        """Create a mock request with the specified attributes."""
        request = MagicMock()

        # Set up url_for
        url_mock = MagicMock()
        url_mock.path = url_for_result
        request.url_for = MagicMock(return_value=url_mock)

        return request

    def test_generates_url_for_specific_language(self):
        """Generates URL prefixed with specified language."""
        request = self._mock_request(url_for_result="/dashboard")

        result = url_for_language(request, "ca", "dashboard")

        assert result == "/ca/dashboard"
        request.url_for.assert_called_once_with("dashboard")

    def test_different_language_codes(self):
        """Works with different language codes."""
        request = self._mock_request(url_for_result="/privacy")

        assert url_for_language(request, "en", "privacy") == "/en/privacy"
        assert url_for_language(request, "es", "privacy") == "/es/privacy"
        assert url_for_language(request, "ca", "privacy") == "/ca/privacy"

    def test_with_path_params(self):
        """Passes path parameters to url_for."""
        request = self._mock_request(url_for_result="/users/123")

        result = url_for_language(request, "en", "user_detail", user_id=123)

        assert result == "/en/users/123"
        request.url_for.assert_called_once_with("user_detail", user_id=123)

    def test_root_path(self):
        """Handles root path correctly."""
        request = self._mock_request(url_for_result="/")

        result = url_for_language(request, "ca", "homepage")

        assert result == "/ca/"


class TestLangUrlFor:
    """Test lang_url_for template helper."""

    def _mock_request(self, language: str = "en", url_for_result: str = "/dashboard"):
        """Create a mock request with the specified attributes."""
        request = MagicMock()

        # Set up state
        state = MagicMock()
        state.language = language
        request.state = state

        # Set up url_for
        url_mock = MagicMock()
        url_mock.path = url_for_result
        request.url_for = MagicMock(return_value=url_mock)

        return request

    def test_basic_url_generation(self):
        """Generates prefixed URL for basic route."""
        request = self._mock_request(language="ca", url_for_result="/dashboard")

        result = lang_url_for(request, "dashboard")

        assert result == "/ca/dashboard"
        request.url_for.assert_called_once_with("dashboard")

    def test_url_with_path_params(self):
        """Generates prefixed URL with path parameters."""
        request = self._mock_request(language="es", url_for_result="/users/123")

        result = lang_url_for(request, "user_detail", user_id=123)

        assert result == "/es/users/123"
        request.url_for.assert_called_once_with("user_detail", user_id=123)

    def test_different_languages(self):
        """Uses request language for prefix."""
        request_en = self._mock_request(language="en", url_for_result="/privacy")
        request_ca = self._mock_request(language="ca", url_for_result="/privacy")

        result_en = lang_url_for(request_en, "privacy")
        result_ca = lang_url_for(request_ca, "privacy")

        assert result_en == "/en/privacy"
        assert result_ca == "/ca/privacy"

    def test_root_path(self):
        """Handles root path correctly."""
        request = self._mock_request(language="ca", url_for_result="/")

        result = lang_url_for(request, "homepage")

        assert result == "/ca/"


class TestHreflangTags:
    """Test hreflang_tags template helper."""

    def _mock_request(
        self,
        path: str = "/privacy",
        base_url: str = "https://example.com",
        has_lang_prefix: bool = False,
        lang_prefix: str = "en",
        original_path: str | None = None,
    ):
        """Create a mock request with the specified attributes."""
        request = MagicMock()

        # Set up URL
        url = MagicMock()
        url.path = path
        request.url = url

        # Set up base_url
        request.base_url = base_url

        # Set up state
        state = MagicMock()
        if has_lang_prefix:
            state.lang_prefix = lang_prefix
            state.original_path = original_path or f"/{lang_prefix}{path}"
        else:
            del state.lang_prefix
        request.state = state

        return request

    def test_generates_tags_for_all_languages(self):
        """Generates hreflang tags for all supported languages."""
        request = self._mock_request(path="/privacy")
        supported = {"en", "ca", "es"}

        result = hreflang_tags(request, supported, "en")

        assert (
            '<link rel="alternate" hreflang="ca" href="https://example.com/ca/privacy" />'
            in result
        )
        assert (
            '<link rel="alternate" hreflang="en" href="https://example.com/en/privacy" />'
            in result
        )
        assert (
            '<link rel="alternate" hreflang="es" href="https://example.com/es/privacy" />'
            in result
        )

    def test_includes_x_default_unprefixed(self):
        """Includes x-default tag pointing to unprefixed URL."""
        request = self._mock_request(path="/privacy")
        supported = {"en", "ca"}

        result = hreflang_tags(request, supported, "en")

        assert (
            '<link rel="alternate" hreflang="x-default" href="https://example.com/privacy" />'
            in result
        )

    def test_x_default_is_unprefixed_regardless_of_default_lang(self):
        """x-default always points to unprefixed URL, not default language."""
        request = self._mock_request(path="/terms")
        supported = {"en", "ca"}

        result = hreflang_tags(request, supported, "ca")

        # x-default should be unprefixed, not /ca/terms
        assert (
            '<link rel="alternate" hreflang="x-default" href="https://example.com/terms" />'
            in result
        )

    def test_handles_prefixed_path(self):
        """Correctly handles requests that arrived with language prefix."""
        request = self._mock_request(
            path="/privacy",  # Middleware stripped prefix
            has_lang_prefix=True,
            lang_prefix="ca",
            original_path="/ca/privacy",
        )
        supported = {"en", "ca"}

        result = hreflang_tags(request, supported, "en")

        # Should generate URLs with /privacy (base path), not /ca/privacy
        assert (
            '<link rel="alternate" hreflang="ca" href="https://example.com/ca/privacy" />'
            in result
        )
        assert (
            '<link rel="alternate" hreflang="en" href="https://example.com/en/privacy" />'
            in result
        )

    def test_output_is_sorted(self):
        """Tags are sorted alphabetically by language code."""
        request = self._mock_request(path="/about")
        supported = {"zh", "en", "ca", "es", "fr"}

        result = hreflang_tags(request, supported, "en")
        lines = result.strip().split("\n")

        # First 5 lines should be language tags in alphabetical order
        assert 'hreflang="ca"' in lines[0]
        assert 'hreflang="en"' in lines[1]
        assert 'hreflang="es"' in lines[2]
        assert 'hreflang="fr"' in lines[3]
        assert 'hreflang="zh"' in lines[4]
        # Last line should be x-default
        assert 'hreflang="x-default"' in lines[5]

    def test_handles_base_url_with_trailing_slash(self):
        """Handles base URL that has trailing slash."""
        request = self._mock_request(path="/page", base_url="https://example.com/")
        supported = {"en"}

        result = hreflang_tags(request, supported, "en")

        assert "https://example.com/en/page" in result
        assert "https://example.com//en/page" not in result

    def test_handles_root_path(self):
        """Handles root path correctly."""
        request = self._mock_request(path="/")
        supported = {"en", "ca"}

        result = hreflang_tags(request, supported, "en")

        assert (
            '<link rel="alternate" hreflang="en" href="https://example.com/en/" />'
            in result
        )
        assert (
            '<link rel="alternate" hreflang="ca" href="https://example.com/ca/" />'
            in result
        )
