# ABOUTME: Tests for register_globals(), register_context_provider(), and _LazyContext
# ABOUTME: Verifies static globals, dynamic providers, lazy evaluation, and request passthrough
# ruff: noqa: S101

from typing import Any
from unittest.mock import MagicMock

from vibetuner.rendering import (
    _build_context,
    _call_provider,
    _context_providers,
    _LazyContext,
    _template_globals,
    register_context_provider,
    register_globals,
)


def _reset():
    """Clear registered globals and providers between tests."""
    _template_globals.clear()
    _context_providers.clear()


def _mock_request(language: str = "en") -> MagicMock:
    request = MagicMock()
    request.state.language = language
    return request


# ---------------------------------------------------------------------------
# register_globals
# ---------------------------------------------------------------------------


class TestRegisterGlobals:
    def setup_method(self):
        _reset()

    def teardown_method(self):
        _reset()

    def test_adds_to_context(self):
        register_globals({"site_title": "My App"})
        assert _template_globals == {"site_title": "My App"}

    def test_merges_multiple_calls(self):
        register_globals({"a": 1})
        register_globals({"b": 2})
        assert _template_globals == {"a": 1, "b": 2}

    def test_later_call_overrides(self):
        register_globals({"key": "old"})
        register_globals({"key": "new"})
        assert _template_globals["key"] == "new"


# ---------------------------------------------------------------------------
# register_context_provider
# ---------------------------------------------------------------------------


class TestRegisterContextProvider:
    def setup_method(self):
        _reset()

    def teardown_method(self):
        _reset()

    def test_bare_decorator(self):
        @register_context_provider
        def my_provider() -> dict[str, Any]:
            return {"x": 1}

        assert my_provider in _context_providers

    def test_decorator_with_parens(self):
        @register_context_provider()
        def my_provider() -> dict[str, Any]:
            return {"x": 1}

        assert my_provider in _context_providers

    def test_returns_original_function(self):
        @register_context_provider
        def my_provider() -> dict[str, Any]:
            return {"x": 1}

        assert my_provider() == {"x": 1}


# ---------------------------------------------------------------------------
# _call_provider (request introspection)
# ---------------------------------------------------------------------------


class TestCallProvider:
    def test_no_arg_provider(self):
        def provider():
            return {"key": "value"}

        result = _call_provider(provider, _mock_request())
        assert result == {"key": "value"}

    def test_request_arg_provider(self):
        def provider(request):
            return {"lang": request.state.language}

        result = _call_provider(provider, _mock_request("ca"))
        assert result == {"lang": "ca"}

    def test_request_kwarg_provider(self):
        from fastapi import Request

        def provider(*, request: Request) -> dict[str, Any]:
            return {"has_request": True}

        result = _call_provider(provider, _mock_request())
        assert result == {"has_request": True}


# ---------------------------------------------------------------------------
# _LazyContext
# ---------------------------------------------------------------------------


class TestLazyContext:
    def test_base_keys_accessible(self):
        ctx = _LazyContext({"a": 1}, [], _mock_request())
        assert ctx["a"] == 1

    def test_providers_not_called_if_key_present(self):
        call_count = 0

        def provider():
            nonlocal call_count
            call_count += 1
            return {"a": "from_provider"}

        ctx = _LazyContext({"a": "from_base"}, [provider], _mock_request())
        assert ctx["a"] == "from_base"
        assert call_count == 0  # provider was never called

    def test_providers_called_on_missing_key(self):
        def provider():
            return {"lazy_key": "lazy_value"}

        ctx = _LazyContext({"a": 1}, [provider], _mock_request())
        assert ctx["lazy_key"] == "lazy_value"

    def test_providers_called_only_once(self):
        call_count = 0

        def provider():
            nonlocal call_count
            call_count += 1
            return {"x": call_count}

        ctx = _LazyContext({}, [provider], _mock_request())
        assert ctx["x"] == 1
        # Access again — should be cached
        try:
            ctx["missing_key"]
        except KeyError:
            pass
        assert call_count == 1

    def test_provider_does_not_override_base(self):
        def provider():
            return {"key": "from_provider", "extra": "yes"}

        ctx = _LazyContext({"key": "from_base"}, [provider], _mock_request())
        # Trigger provider resolution by accessing a provider-only key
        assert ctx["extra"] == "yes"
        # Base key should NOT be overridden by provider
        assert ctx["key"] == "from_base"

    def test_provider_receives_request(self):
        def provider(request):
            return {"lang": request.state.language}

        ctx = _LazyContext({}, [provider], _mock_request("es"))
        assert ctx["lang"] == "es"

    def test_multiple_providers(self):
        def provider_a():
            return {"a": 1}

        def provider_b():
            return {"b": 2}

        ctx = _LazyContext({}, [provider_a, provider_b], _mock_request())
        assert ctx["a"] == 1
        assert ctx["b"] == 2

    def test_provider_error_is_caught(self):
        def bad_provider():
            raise RuntimeError("boom")

        ctx = _LazyContext({}, [bad_provider], _mock_request())
        # Accessing a missing key should raise KeyError, not RuntimeError
        try:
            ctx["nonexistent"]
        except KeyError:
            pass  # expected

    def test_provider_non_dict_is_skipped(self):
        def bad_provider():
            return "not a dict"

        ctx = _LazyContext({}, [bad_provider], _mock_request())
        try:
            ctx["missing"]
        except KeyError:
            pass  # expected

    def test_keyerror_for_truly_missing_key(self):
        def provider():
            return {"known": True}

        ctx = _LazyContext({}, [provider], _mock_request())
        try:
            ctx["unknown"]
            raise AssertionError("Should have raised KeyError")
        except KeyError:
            pass


# ---------------------------------------------------------------------------
# _build_context integration
# ---------------------------------------------------------------------------


class TestBuildContext:
    def setup_method(self):
        _reset()

    def teardown_method(self):
        _reset()

    def _mock_data_ctx(self, monkeypatch):
        """Patch data_ctx to avoid importing the real context module."""
        mock_ctx = MagicMock()
        mock_ctx.model_dump.return_value = {"DEBUG": False, "project_name": "test"}
        mock_ctx.default_language = "en"
        monkeypatch.setattr("vibetuner.rendering.data_ctx", mock_ctx)
        return mock_ctx

    def test_base_context_without_providers(self, monkeypatch):
        self._mock_data_ctx(monkeypatch)
        request = _mock_request("ca")
        ctx = _build_context(request)
        assert isinstance(ctx, dict)
        assert not isinstance(ctx, _LazyContext)
        assert ctx["language"] == "ca"
        assert ctx["DEBUG"] is False

    def test_returns_lazy_context_with_providers(self, monkeypatch):
        self._mock_data_ctx(monkeypatch)

        @register_context_provider
        def provider():
            return {"extra": True}

        request = _mock_request()
        ctx = _build_context(request)
        assert isinstance(ctx, _LazyContext)

    def test_globals_in_build_context(self, monkeypatch):
        self._mock_data_ctx(monkeypatch)
        register_globals({"site_title": "Test"})
        request = _mock_request()
        ctx = _build_context(request)
        assert ctx["site_title"] == "Test"

    def test_user_ctx_overrides_globals(self, monkeypatch):
        self._mock_data_ctx(monkeypatch)
        register_globals({"site_title": "Default"})
        request = _mock_request()
        ctx = _build_context(request, {"site_title": "Custom"})
        assert ctx["site_title"] == "Custom"

    def test_user_ctx_overrides_provider(self, monkeypatch):
        self._mock_data_ctx(monkeypatch)

        @register_context_provider
        def provider():
            return {"key": "from_provider"}

        request = _mock_request()
        ctx = _build_context(request, {"key": "from_user"})
        # User ctx is in base, provider should not override
        assert ctx["key"] == "from_user"

    def test_provider_receives_request_via_build_context(self, monkeypatch):
        self._mock_data_ctx(monkeypatch)

        @register_context_provider
        def provider(request):
            return {"lang": request.state.language}

        request = _mock_request("fr")
        ctx = _build_context(request)
        assert ctx["lang"] == "fr"
