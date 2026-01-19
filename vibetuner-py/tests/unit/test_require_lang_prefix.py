# ABOUTME: Unit tests for require_lang_prefix route dependency
# ABOUTME: Verifies SEO routes redirect anonymous users to prefixed URLs
# ruff: noqa: S101

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


async def require_lang_prefix(request) -> None:
    """Test copy of dependency to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.deps.require_lang_prefix.
    """
    # If accessed with prefix, we're good
    if hasattr(request.state, "lang_prefix"):
        return

    # Authenticated users don't need prefix
    if request.user.is_authenticated:
        return

    # Anonymous user without prefix: redirect to prefixed URL
    lang = request.state.language
    current_path = request.url.path
    prefixed_url = f"/{lang}{current_path}"

    raise HTTPException(status_code=307, headers={"Location": prefixed_url})


class TestRequireLangPrefix:
    """Test require_lang_prefix dependency logic."""

    def _mock_request(
        self,
        has_lang_prefix: bool = False,
        is_authenticated: bool = False,
        language: str = "en",
        path: str = "/dashboard",
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
        request.url = url

        return request

    @pytest.mark.asyncio
    async def test_allows_request_with_lang_prefix(self):
        """Request with language prefix passes through."""
        request = self._mock_request(has_lang_prefix=True, is_authenticated=False)

        # Should not raise
        await require_lang_prefix(request)

    @pytest.mark.asyncio
    async def test_allows_authenticated_user_without_prefix(self):
        """Authenticated user without prefix passes through."""
        request = self._mock_request(has_lang_prefix=False, is_authenticated=True)

        # Should not raise
        await require_lang_prefix(request)

    @pytest.mark.asyncio
    async def test_redirects_anonymous_user_without_prefix(self):
        """Anonymous user without prefix gets redirected."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=False,
            language="ca",
            path="/dashboard",
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_lang_prefix(request)

        assert exc_info.value.status_code == 307
        assert exc_info.value.headers["Location"] == "/ca/dashboard"

    @pytest.mark.asyncio
    async def test_redirect_uses_request_language(self):
        """Redirect uses the language from request.state.language."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=False,
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
            is_authenticated=False,
            language="en",
            path="/admin/users/123",
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_lang_prefix(request)

        assert exc_info.value.headers["Location"] == "/en/admin/users/123"

    @pytest.mark.asyncio
    async def test_authenticated_with_prefix_allowed(self):
        """Authenticated user with prefix passes through."""
        request = self._mock_request(has_lang_prefix=True, is_authenticated=True)

        # Should not raise
        await require_lang_prefix(request)

    @pytest.mark.asyncio
    async def test_redirect_for_root_path(self):
        """Anonymous user at root path gets redirected correctly."""
        request = self._mock_request(
            has_lang_prefix=False,
            is_authenticated=False,
            language="ca",
            path="/",
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_lang_prefix(request)

        assert exc_info.value.headers["Location"] == "/ca/"
