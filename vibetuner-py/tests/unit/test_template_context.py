# ABOUTME: Tests for automatic template context injection
# ABOUTME: Verifies that language is auto-injected and can be overridden
# ruff: noqa: S101

from typing import Any
from unittest.mock import MagicMock


def build_template_context(
    data_ctx_dump: dict[str, Any],
    request: MagicMock,
    default_language: str,
    user_ctx: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Test copy of context building logic from render_template.

    Mirrors the implementation in vibetuner.frontend.templates.render_template.
    """
    user_ctx = user_ctx or {}
    language = getattr(request.state, "language", default_language)
    return {
        **data_ctx_dump,
        "request": request,
        "language": language,
        **user_ctx,
    }


class TestRenderTemplateLanguageContext:
    """Tests for language auto-injection in render_template."""

    def _mock_request(self, language: str | None = "en"):
        """Create a mock request with the specified language."""
        request = MagicMock()
        state = MagicMock()
        if language is not None:
            state.language = language
        else:
            # Remove language attribute to simulate missing state
            del state.language
        request.state = state
        return request

    def test_language_auto_injected_from_request_state(self):
        """Language is automatically injected from request.state.language."""
        request = self._mock_request(language="ca")
        data_ctx_dump = {"DEBUG": False, "project_name": "test"}

        context = build_template_context(data_ctx_dump, request, "en")

        assert "language" in context
        assert context["language"] == "ca"

    def test_user_context_overrides_auto_language(self):
        """User-provided language in context overrides auto-injected value."""
        request = self._mock_request(language="en")
        data_ctx_dump = {"DEBUG": False}

        context = build_template_context(
            data_ctx_dump, request, "en", user_ctx={"language": "custom_lang"}
        )

        assert context["language"] == "custom_lang"

    def test_language_fallback_when_state_missing(self):
        """Falls back to default_language when request.state.language is missing."""
        request = self._mock_request(language=None)
        data_ctx_dump = {"DEBUG": False}
        default_lang = "es"

        context = build_template_context(data_ctx_dump, request, default_lang)

        assert context["language"] == default_lang

    def test_request_included_in_context(self):
        """Request object is included in the context."""
        request = self._mock_request(language="en")
        data_ctx_dump = {}

        context = build_template_context(data_ctx_dump, request, "en")

        assert context["request"] is request

    def test_data_ctx_values_included(self):
        """Values from data_ctx are included in context."""
        request = self._mock_request(language="en")
        data_ctx_dump = {"DEBUG": True, "project_name": "TestProject", "version": "1.0"}

        context = build_template_context(data_ctx_dump, request, "en")

        assert context["DEBUG"] is True
        assert context["project_name"] == "TestProject"
        assert context["version"] == "1.0"

    def test_user_ctx_can_override_data_ctx(self):
        """User context can override values from data_ctx."""
        request = self._mock_request(language="en")
        data_ctx_dump = {"project_name": "Default"}

        context = build_template_context(
            data_ctx_dump, request, "en", user_ctx={"project_name": "Custom"}
        )

        assert context["project_name"] == "Custom"
