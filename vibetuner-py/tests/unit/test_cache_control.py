# ruff: noqa: S101
"""Tests for the @cache_control decorator."""

import pytest
from starlette.responses import HTMLResponse, JSONResponse
from vibetuner.decorators import cache_control


class TestCacheControl:
    """Test @cache_control decorator."""

    @pytest.mark.asyncio
    async def test_public_max_age(self):
        """Sets public, max-age directive."""

        @cache_control(max_age=300, public=True)
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == "public, max-age=300"

    @pytest.mark.asyncio
    async def test_no_store(self):
        """Sets no-store directive."""

        @cache_control(no_store=True)
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == "no-store"

    @pytest.mark.asyncio
    async def test_private_max_age(self):
        """Sets private, max-age directive."""

        @cache_control(private=True, max_age=60)
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == "private, max-age=60"

    @pytest.mark.asyncio
    async def test_no_cache_max_age_zero(self):
        """Sets no-cache, max-age=0."""

        @cache_control(no_cache=True, max_age=0)
        async def handler():
            return JSONResponse({"data": "value"})

        result = await handler()
        assert result.headers["Cache-Control"] == "no-cache, max-age=0"

    @pytest.mark.asyncio
    async def test_stale_while_revalidate(self):
        """Sets stale-while-revalidate directive."""

        @cache_control(max_age=86400, stale_while_revalidate=3600)
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert (
            result.headers["Cache-Control"]
            == "max-age=86400, stale-while-revalidate=3600"
        )

    @pytest.mark.asyncio
    async def test_s_maxage(self):
        """Sets s-maxage for shared caches."""

        @cache_control(public=True, max_age=300, s_maxage=600)
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == "public, max-age=300, s-maxage=600"

    @pytest.mark.asyncio
    async def test_must_revalidate(self):
        """Sets must-revalidate directive."""

        @cache_control(max_age=0, must_revalidate=True)
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == "must-revalidate, max-age=0"

    @pytest.mark.asyncio
    async def test_immutable(self):
        """Sets immutable directive for versioned assets."""

        @cache_control(max_age=31536000, public=True, immutable=True)
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == "public, immutable, max-age=31536000"

    @pytest.mark.asyncio
    async def test_sync_route(self):
        """Works with sync route functions."""

        @cache_control(max_age=60)
        def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == "max-age=60"

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        """Wrapper preserves the original function name."""

        @cache_control(max_age=60)
        async def my_route():
            return HTMLResponse("<html>ok</html>")

        assert my_route.__name__ == "my_route"

    @pytest.mark.asyncio
    async def test_no_directives(self):
        """Empty cache_control produces empty header value."""

        @cache_control()
        async def handler():
            return HTMLResponse("<html>ok</html>")

        result = await handler()
        assert result.headers["Cache-Control"] == ""
