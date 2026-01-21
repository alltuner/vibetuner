# ABOUTME: Unit tests for deprecated LangPrefixDep route dependency
# ABOUTME: Primary redirect logic is now tested in test_localized_router.py
# ruff: noqa: S101

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


async def require_lang_prefix(request) -> None:
    """Test copy of dependency to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.deps.require_lang_prefix.

    New behavior (BREAKING CHANGE):
    - Anonymous: serve at unprefixed URL (default/detected language)
    - Authenticated: 301 redirect to /{lang}/{path}
    """
    # If accessed with prefix, we're good
    if hasattr(request.state, "lang_prefix"):
        return

    # Check if endpoint is marked as localized
    endpoint = request.scope.get("endpoint")
    if endpoint and not getattr(endpoint, "_localized", True):
        return  # Non-localized route

    # Anonymous users: no redirect (serve default/detected language)
    if not request.user.is_authenticated:
        return

    # Authenticated user without prefix: 301 redirect to prefixed URL
    lang = request.state.language
    prefixed_url = f"/{lang}{request.url.path}"
    if request.url.query:
        prefixed_url += f"?{request.url.query}"

    raise HTTPException(status_code=301, headers={"Location": prefixed_url})


class TestRequireLangPrefix:
    """Test require_lang_prefix dependency logic.

    New behavior (BREAKING CHANGE):
    - Anonymous: serve at unprefixed URL (no redirect)
    - Authenticated: 301 redirect to /{lang}/{path}
    """

    def _mock_request(
        self,
        has_lang_prefix: bool = False,
        is_authenticated: bool = False,
        language: str = "en",
        path: str = "/dashboard",
        query: str = "",
        endpoint_localized: bool | None = None,
    ) -> MagicMock:
        """Create a mock request with the specified attributes."""
        request = MagicMock()

        # Set up state
        state = MagicMock()
        state.language = language
        if has_lang_prefix:
            state.lang_prefix = language
        else:
            del state.lang_prefix  # Remove the attribute
        request.state = state

        # Set up user
        user = MagicMock()
        user.is_authenticated = is_authenticated
        request.user = user

        # Set up URL
        url = MagicMock()
        url.path = path
        url.query = query
        request.url = url

        # Set up scope with endpoint
        endpoint = MagicMock()
        if endpoint_localized is not None:
            endpoint._localized = endpoint_localized
        else:
            del endpoint._localized
        request.scope = {"endpoint": endpoint}

        return request

    @pytest.mark.asyncio
    async def test_allows_request_with_lang_prefix(self):
        """Request with language prefix passes through."""
        request = self._mock_request(has_lang_prefix=True, is_authenticated=False)

        # Should not raise
        await require_lang_prefix(request)

    @pytest.mark.asyncio
    async def test_anonymous_user_without_prefix_serves_content(self):
        """Anonymous user without prefix serves content (no redirect)."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=False,
            language="ca",
            path="/dashboard",
        )

        # Should not raise - serves content at unprefixed URL
        await require_lang_prefix(request)

    @pytest.mark.asyncio
    async def test_authenticated_user_without_prefix_redirects(self):
        """Authenticated user without prefix gets 301 redirect."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=True,
            language="ca",
            path="/dashboard",
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_lang_prefix(request)

        assert exc_info.value.status_code == 301
        assert exc_info.value.headers["Location"] == "/ca/dashboard"

    @pytest.mark.asyncio
    async def test_redirect_uses_request_language(self):
        """Redirect uses the language from request.state.language."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=True,
            language="es",
            path="/privacy",
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_lang_prefix(request)

        assert exc_info.value.headers["Location"] == "/es/privacy"

    @pytest.mark.asyncio
    async def test_redirect_preserves_full_path(self):
        """Redirect preserves the full URL path."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=True,
            language="en",
            path="/admin/users/123",
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_lang_prefix(request)

        assert exc_info.value.headers["Location"] == "/en/admin/users/123"

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
            await require_lang_prefix(request)

        assert exc_info.value.headers["Location"] == "/en/search?q=test&page=2"

    @pytest.mark.asyncio
    async def test_authenticated_with_prefix_allowed(self):
        """Authenticated user with prefix passes through."""
        request = self._mock_request(has_lang_prefix=True, is_authenticated=True)

        # Should not raise
        await require_lang_prefix(request)

    @pytest.mark.asyncio
    async def test_anonymous_at_root_serves_content(self):
        """Anonymous user at root path serves content (no redirect)."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=False,
            language="ca",
            path="/",
        )

        # Should not raise - serves content at unprefixed URL
        await require_lang_prefix(request)

    @pytest.mark.asyncio
    async def test_non_localized_endpoint_no_redirect(self):
        """Non-localized endpoint does not redirect authenticated users."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=True,
            language="ca",
            path="/api/users",
            endpoint_localized=False,
        )

        # Should not raise - endpoint is marked as non-localized
        await require_lang_prefix(request)
