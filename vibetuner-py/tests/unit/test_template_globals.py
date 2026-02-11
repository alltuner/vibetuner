# ABOUTME: Tests for register_globals() and register_context_provider()
# ABOUTME: Verifies that app-level context is merged into every render call
# ruff: noqa: S101

from typing import Any
from unittest.mock import MagicMock

from vibetuner.rendering import (
    _collect_provider_context,
    _context_providers,
    _template_globals,
    register_context_provider,
    register_globals,
)


def _reset_globals():
    """Clear registered globals and providers between tests."""
    _template_globals.clear()
    _context_providers.clear()


class TestRegisterGlobals:
    """Tests for register_globals()."""

    def setup_method(self):
        _reset_globals()

    def teardown_method(self):
        _reset_globals()

    def test_register_globals_adds_to_context(self):
        register_globals({"site_title": "My App"})
        assert _template_globals == {"site_title": "My App"}

    def test_register_globals_merges_multiple_calls(self):
        register_globals({"site_title": "My App"})
        register_globals({"og_image": "/static/og.png"})
        assert _template_globals == {
            "site_title": "My App",
            "og_image": "/static/og.png",
        }

    def test_register_globals_later_call_overrides(self):
        register_globals({"site_title": "Old"})
        register_globals({"site_title": "New"})
        assert _template_globals["site_title"] == "New"


class TestRegisterContextProvider:
    """Tests for register_context_provider()."""

    def setup_method(self):
        _reset_globals()

    def teardown_method(self):
        _reset_globals()

    def test_decorator_without_parens(self):
        @register_context_provider
        def my_provider() -> dict[str, Any]:
            return {"key": "value"}

        assert my_provider in _context_providers

    def test_decorator_with_parens(self):
        @register_context_provider()
        def my_provider() -> dict[str, Any]:
            return {"key": "value"}

        assert my_provider in _context_providers

    def test_provider_returns_original_function(self):
        @register_context_provider
        def my_provider() -> dict[str, Any]:
            return {"key": "value"}

        assert my_provider() == {"key": "value"}


class TestCollectProviderContext:
    """Tests for _collect_provider_context()."""

    def setup_method(self):
        _reset_globals()

    def teardown_method(self):
        _reset_globals()

    def test_collects_from_single_provider(self):
        @register_context_provider
        def provider() -> dict[str, Any]:
            return {"a": 1}

        result = _collect_provider_context()
        assert result == {"a": 1}

    def test_collects_from_multiple_providers(self):
        @register_context_provider
        def provider_a() -> dict[str, Any]:
            return {"a": 1}

        @register_context_provider
        def provider_b() -> dict[str, Any]:
            return {"b": 2}

        result = _collect_provider_context()
        assert result == {"a": 1, "b": 2}

    def test_later_provider_overrides_earlier(self):
        @register_context_provider
        def provider_a() -> dict[str, Any]:
            return {"key": "first"}

        @register_context_provider
        def provider_b() -> dict[str, Any]:
            return {"key": "second"}

        result = _collect_provider_context()
        assert result["key"] == "second"

    def test_provider_error_is_caught(self):
        @register_context_provider
        def bad_provider() -> dict[str, Any]:
            raise RuntimeError("boom")

        result = _collect_provider_context()
        assert result == {}

    def test_provider_returning_non_dict_is_skipped(self):
        @register_context_provider
        def bad_provider():
            return "not a dict"

        result = _collect_provider_context()
        assert result == {}

    def test_empty_providers_returns_empty_dict(self):
        result = _collect_provider_context()
        assert result == {}


class TestContextMergeOrder:
    """Tests that globals and providers merge correctly with render context."""

    def setup_method(self):
        _reset_globals()

    def teardown_method(self):
        _reset_globals()

    def _build_merged_context(
        self,
        data_ctx_dump: dict[str, Any],
        request: MagicMock,
        default_language: str,
        user_ctx: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Mirrors the merge logic in render_template."""
        user_ctx = user_ctx or {}
        language = getattr(request.state, "language", default_language)
        return {
            **data_ctx_dump,
            **_template_globals,
            **_collect_provider_context(),
            "request": request,
            "language": language,
            **user_ctx,
        }

    def _mock_request(self, language: str = "en") -> MagicMock:
        request = MagicMock()
        request.state.language = language
        return request

    def test_globals_available_in_context(self):
        register_globals({"site_title": "Test"})
        request = self._mock_request()
        ctx = self._build_merged_context({}, request, "en")
        assert ctx["site_title"] == "Test"

    def test_provider_available_in_context(self):
        @register_context_provider
        def provider() -> dict[str, Any]:
            return {"nav_items": ["home", "about"]}

        request = self._mock_request()
        ctx = self._build_merged_context({}, request, "en")
        assert ctx["nav_items"] == ["home", "about"]

    def test_user_ctx_overrides_globals(self):
        register_globals({"site_title": "Default"})
        request = self._mock_request()
        ctx = self._build_merged_context(
            {}, request, "en", user_ctx={"site_title": "Override"}
        )
        assert ctx["site_title"] == "Override"

    def test_user_ctx_overrides_provider(self):
        @register_context_provider
        def provider() -> dict[str, Any]:
            return {"key": "from_provider"}

        request = self._mock_request()
        ctx = self._build_merged_context(
            {}, request, "en", user_ctx={"key": "from_user"}
        )
        assert ctx["key"] == "from_user"

    def test_provider_overrides_globals(self):
        register_globals({"key": "from_globals"})

        @register_context_provider
        def provider() -> dict[str, Any]:
            return {"key": "from_provider"}

        request = self._mock_request()
        ctx = self._build_merged_context({}, request, "en")
        assert ctx["key"] == "from_provider"
