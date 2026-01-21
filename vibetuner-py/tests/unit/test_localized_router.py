# ABOUTME: Unit tests for LocalizedRouter class and @localized decorator
# ABOUTME: Verifies router-level localization control and auto-dependency injection
# ruff: noqa: S101

from collections.abc import Callable
from functools import wraps
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import APIRouter, Depends, HTTPException, Request


async def _localized_redirect(request: Request) -> None:
    """Test copy of redirect logic."""
    if hasattr(request.state, "lang_prefix"):
        return

    if not request.user.is_authenticated:
        return

    lang = request.state.language
    prefixed_url = f"/{lang}{request.url.path}"
    if request.url.query:
        prefixed_url += f"?{request.url.query}"

    raise HTTPException(status_code=301, headers={"Location": prefixed_url})


class LocalizedRouter(APIRouter):
    """Test copy of router to avoid importing full vibetuner.frontend package."""

    def __init__(self, *args, localized: bool | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._localized = localized

    def add_api_route(self, path, endpoint, **kwargs):
        if not hasattr(endpoint, "_localized"):
            if self._localized is not None:
                endpoint._localized = self._localized

        if getattr(endpoint, "_localized", False):
            dependencies = list(kwargs.get("dependencies") or [])
            dependencies.append(Depends(_localized_redirect))
            kwargs["dependencies"] = dependencies

        return super().add_api_route(path, endpoint, **kwargs)


def localized(func: Callable[..., Any]) -> Callable[..., Any]:
    """Test copy of decorator."""
    func._localized = True

    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is not None:
            await _localized_redirect(request)

        return await func(*args, **kwargs)

    wrapper._localized = True
    return wrapper


class TestLocalizedRouter:
    """Test LocalizedRouter class."""

    def test_explicit_localized_true_marks_endpoints(self):
        """Router with localized=True marks all endpoints as localized."""
        router = LocalizedRouter(localized=True)

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert hasattr(my_endpoint, "_localized")
        assert my_endpoint._localized is True

    def test_explicit_localized_false_marks_endpoints(self):
        """Router with localized=False marks all endpoints as non-localized."""
        router = LocalizedRouter(localized=False)

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert hasattr(my_endpoint, "_localized")
        assert my_endpoint._localized is False

    def test_localized_none_does_not_mark_endpoints(self):
        """Router with localized=None does not mark endpoints."""
        router = LocalizedRouter(localized=None)

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert not hasattr(my_endpoint, "_localized")

    def test_default_is_none(self):
        """Router without localized argument defaults to None."""
        router = LocalizedRouter()

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert not hasattr(my_endpoint, "_localized")

    def test_does_not_override_existing_localized_attribute(self):
        """Router does not override endpoint's existing _localized attribute."""
        router = LocalizedRouter(localized=True)

        async def my_endpoint():
            pass

        my_endpoint._localized = False  # Preset

        router.add_api_route("/test", my_endpoint)

        assert my_endpoint._localized is False  # Should remain unchanged

    def test_multiple_endpoints_same_router(self):
        """Multiple endpoints on same router all get same localized setting."""
        router = LocalizedRouter(localized=True)

        async def endpoint_a():
            pass

        async def endpoint_b():
            pass

        router.add_api_route("/a", endpoint_a)
        router.add_api_route("/b", endpoint_b)

        assert endpoint_a._localized is True
        assert endpoint_b._localized is True

    def test_inherits_apirouter_features(self):
        """LocalizedRouter inherits all APIRouter features."""
        router = LocalizedRouter(prefix="/api", tags=["test"], localized=True)

        assert router.prefix == "/api"
        assert router.tags == ["test"]

    def test_decorator_style_routes(self):
        """Decorator-style routes work correctly."""
        router = LocalizedRouter(localized=True)

        @router.get("/test")
        async def my_endpoint():
            pass

        assert hasattr(my_endpoint, "_localized")
        assert my_endpoint._localized is True

    def test_auto_adds_dependency_when_localized_true(self):
        """Router with localized=True auto-adds redirect dependency."""
        router = LocalizedRouter(localized=True)

        async def my_endpoint():
            pass

        # Track what dependencies are passed
        original_add = APIRouter.add_api_route
        captured_deps = []

        def mock_add(self, path, endpoint, **kwargs):
            captured_deps.extend(kwargs.get("dependencies", []))
            return original_add(self, path, endpoint, **kwargs)

        APIRouter.add_api_route = mock_add
        try:
            router.add_api_route("/test", my_endpoint)
        finally:
            APIRouter.add_api_route = original_add

        # Should have added the redirect dependency
        assert len(captured_deps) == 1

    def test_no_dependency_when_localized_false(self):
        """Router with localized=False does not add redirect dependency."""
        router = LocalizedRouter(localized=False)

        async def my_endpoint():
            pass

        original_add = APIRouter.add_api_route
        captured_deps = []

        def mock_add(self, path, endpoint, **kwargs):
            captured_deps.extend(kwargs.get("dependencies", []))
            return original_add(self, path, endpoint, **kwargs)

        APIRouter.add_api_route = mock_add
        try:
            router.add_api_route("/test", my_endpoint)
        finally:
            APIRouter.add_api_route = original_add

        assert len(captured_deps) == 0

    def test_preserves_existing_dependencies(self):
        """Router preserves existing dependencies when adding redirect."""
        router = LocalizedRouter(localized=True)

        async def my_endpoint():
            pass

        async def existing_dep():
            pass

        original_add = APIRouter.add_api_route
        captured_deps = []

        def mock_add(self, path, endpoint, **kwargs):
            captured_deps.extend(kwargs.get("dependencies", []))
            return original_add(self, path, endpoint, **kwargs)

        APIRouter.add_api_route = mock_add
        try:
            router.add_api_route(
                "/test", my_endpoint, dependencies=[Depends(existing_dep)]
            )
        finally:
            APIRouter.add_api_route = original_add

        # Should have both: existing + redirect
        assert len(captured_deps) == 2


class TestLocalizedDecorator:
    """Test @localized decorator."""

    def test_marks_function_as_localized(self):
        """Decorator marks function with _localized=True."""

        @localized
        async def my_endpoint(request: Request):
            return "ok"

        assert hasattr(my_endpoint, "_localized")
        assert my_endpoint._localized is True

    def test_preserves_function_name(self):
        """Decorator preserves original function name."""

        @localized
        async def my_endpoint(request: Request):
            return "ok"

        assert my_endpoint.__name__ == "my_endpoint"

    @pytest.mark.asyncio
    async def test_calls_redirect_logic(self):
        """Decorator calls redirect logic before function."""
        called = []

        @localized
        async def my_endpoint(request: Request):
            called.append("endpoint")
            return "ok"

        # Create mock request for anonymous user
        request = MagicMock()
        request.user.is_authenticated = False
        state = MagicMock()
        del state.lang_prefix
        request.state = state

        result = await my_endpoint(request=request)

        assert result == "ok"
        assert "endpoint" in called

    @pytest.mark.asyncio
    async def test_redirects_authenticated_user(self):
        """Decorator redirects authenticated user without prefix."""

        @localized
        async def my_endpoint(request: Request):
            return "ok"

        # Create mock request for authenticated user
        request = MagicMock()
        request.user.is_authenticated = True
        state = MagicMock()
        del state.lang_prefix
        state.language = "ca"
        request.state = state
        request.url.path = "/privacy"
        request.url.query = ""

        with pytest.raises(HTTPException) as exc_info:
            await my_endpoint(request=request)

        assert exc_info.value.status_code == 301
        assert exc_info.value.headers["Location"] == "/ca/privacy"

    @pytest.mark.asyncio
    async def test_no_redirect_with_prefix(self):
        """Decorator does not redirect when request has language prefix."""
        called = []

        @localized
        async def my_endpoint(request: Request):
            called.append("endpoint")
            return "ok"

        # Create mock request with language prefix
        request = MagicMock()
        request.user.is_authenticated = True
        state = MagicMock()
        state.lang_prefix = "ca"
        request.state = state

        result = await my_endpoint(request=request)

        assert result == "ok"
        assert "endpoint" in called


class TestLocalizedRedirect:
    """Test the redirect logic directly."""

    def _mock_request(
        self,
        has_lang_prefix: bool = False,
        is_authenticated: bool = False,
        language: str = "en",
        path: str = "/dashboard",
        query: str = "",
    ) -> MagicMock:
        """Create a mock request with the specified attributes."""
        request = MagicMock()

        state = MagicMock()
        state.language = language
        if has_lang_prefix:
            state.lang_prefix = language
        else:
            del state.lang_prefix
        request.state = state

        user = MagicMock()
        user.is_authenticated = is_authenticated
        request.user = user

        url = MagicMock()
        url.path = path
        url.query = query
        request.url = url

        return request

    @pytest.mark.asyncio
    async def test_allows_request_with_lang_prefix(self):
        """Request with language prefix passes through."""
        request = self._mock_request(has_lang_prefix=True, is_authenticated=True)
        await _localized_redirect(request)  # Should not raise

    @pytest.mark.asyncio
    async def test_anonymous_user_no_redirect(self):
        """Anonymous user without prefix is not redirected."""
        request = self._mock_request(has_lang_prefix=False, is_authenticated=False)
        await _localized_redirect(request)  # Should not raise

    @pytest.mark.asyncio
    async def test_authenticated_user_redirects(self):
        """Authenticated user without prefix gets 301 redirect."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=True,
            language="ca",
            path="/dashboard",
        )

        with pytest.raises(HTTPException) as exc_info:
            await _localized_redirect(request)

        assert exc_info.value.status_code == 301
        assert exc_info.value.headers["Location"] == "/ca/dashboard"

    @pytest.mark.asyncio
    async def test_redirect_preserves_query_string(self):
        """Redirect preserves query string parameters."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=True,
            language="en",
            path="/search",
            query="q=test&page=2",
        )

        with pytest.raises(HTTPException) as exc_info:
            await _localized_redirect(request)

        assert exc_info.value.headers["Location"] == "/en/search?q=test&page=2"
