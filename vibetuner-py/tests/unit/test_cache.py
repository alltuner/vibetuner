# ruff: noqa: S101
"""Tests for the @cache response caching decorator."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from vibetuner.cache import (
    _build_cache_key,
    _restore_response,
    _serialize_response,
    cache,
)


# All decorator tests patch vibetuner.config.settings since cache.py imports it
# lazily inside the wrapper function.
_SETTINGS_PATH = "vibetuner.config.settings"
_GET_CLIENT_PATH = "vibetuner.redis.get_redis_client"
_RESET_CLIENT_PATH = "vibetuner.redis.reset_redis_client"


def _make_request(
    path: str = "/test", query_string: str = "", headers: dict | None = None
):
    """Create a minimal Starlette Request for testing."""
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": query_string.encode(),
        "headers": [
            (k.lower().encode(), v.encode()) for k, v in (headers or {}).items()
        ],
    }
    return Request(scope)


def _mock_settings(
    *, debug: bool = False, redis_url="redis://localhost", redis_key_prefix="test:"
):
    mock = MagicMock()
    mock.debug = debug
    mock.redis_url = redis_url
    mock.redis_key_prefix = redis_key_prefix
    return mock


class TestBuildCacheKey:
    """Test cache key generation."""

    def test_simple_path(self):
        key = _build_cache_key("myapp:dev:", "/api/stats", "")
        assert key.startswith("myapp:dev:cache:")
        assert "/api/stats" in key

    def test_with_query_params(self):
        key = _build_cache_key("myapp:", "/api/stats", "page=1&sort=name")
        assert "page=1&sort=name" in key

    def test_different_paths_different_keys(self):
        key1 = _build_cache_key("p:", "/a", "")
        key2 = _build_cache_key("p:", "/b", "")
        assert key1 != key2

    def test_different_params_different_keys(self):
        key1 = _build_cache_key("p:", "/a", "x=1")
        key2 = _build_cache_key("p:", "/a", "x=2")
        assert key1 != key2


class TestSerializeRestore:
    """Test response serialization round-trips."""

    def test_json_response(self):
        resp = JSONResponse({"users": 42})
        serialized = _serialize_response(resp)
        assert serialized is not None

        restored = _restore_response(serialized)
        assert restored.status_code == 200
        body = json.loads(restored.body)
        assert body == {"users": 42}

    def test_html_response(self):
        resp = HTMLResponse("<h1>Hello</h1>")
        serialized = _serialize_response(resp)
        assert serialized is not None

        restored = _restore_response(serialized)
        assert isinstance(restored, HTMLResponse)
        assert b"Hello" in restored.body

    def test_dict_response(self):
        resp = {"key": "value"}
        serialized = _serialize_response(resp)
        assert serialized is not None

        restored = _restore_response(serialized)
        assert restored == {"key": "value"}

    def test_unsupported_type_returns_none(self):
        assert _serialize_response("plain string") is None


class TestCacheDecorator:
    """Test the @cache decorator behavior."""

    @pytest.mark.asyncio
    async def test_disabled_in_debug_mode(self):
        """Caching is skipped when debug=True."""
        call_count = 0

        @cache(expire=60)
        async def handler(request: Request):
            nonlocal call_count
            call_count += 1
            return JSONResponse({"count": call_count})

        request = _make_request()

        with patch(_SETTINGS_PATH, _mock_settings(debug=True)):
            await handler(request=request)
            await handler(request=request)

        assert call_count == 2  # Called twice, no caching

    @pytest.mark.asyncio
    async def test_force_caching_in_debug(self):
        """force_caching=True enables caching even in debug mode."""
        call_count = 0
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=None)
        mock_client.set = AsyncMock()

        @cache(expire=120, force_caching=True)
        async def handler(request: Request):
            nonlocal call_count
            call_count += 1
            return JSONResponse({"count": call_count})

        request = _make_request()

        with (
            patch(_SETTINGS_PATH, _mock_settings(debug=True)),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=mock_client)),
            patch(_RESET_CLIENT_PATH),
        ):
            await handler(request=request)

        assert call_count == 1
        mock_client.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_redis_url_is_noop(self):
        """When redis_url is None the decorator is a transparent no-op."""
        call_count = 0

        @cache(expire=60)
        async def handler(request: Request):
            nonlocal call_count
            call_count += 1
            return JSONResponse({"ok": True})

        request = _make_request()

        with patch(_SETTINGS_PATH, _mock_settings(redis_url=None)):
            await handler(request=request)
            await handler(request=request)

        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Serves cached response without calling handler."""
        cached_data = json.dumps(
            {
                "type": "json",
                "body": '{"cached": true}',
                "status": 200,
            }
        ).encode()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=cached_data)
        call_count = 0

        @cache(expire=60)
        async def handler(request: Request):
            nonlocal call_count
            call_count += 1
            return JSONResponse({"cached": False})

        request = _make_request()

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=mock_client)),
            patch(_RESET_CLIENT_PATH),
        ):
            result = await handler(request=request)

        assert call_count == 0
        body = json.loads(result.body)
        assert body["cached"] is True

    @pytest.mark.asyncio
    async def test_no_cache_header_bypasses_cache(self):
        """Cache-Control: no-cache header forces re-execution."""
        cached_data = json.dumps(
            {
                "type": "json",
                "body": '{"stale": true}',
                "status": 200,
            }
        ).encode()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=cached_data)
        mock_client.set = AsyncMock()

        @cache(expire=60)
        async def handler(request: Request):
            return JSONResponse({"fresh": True})

        request = _make_request(headers={"Cache-Control": "no-cache"})

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=mock_client)),
            patch(_RESET_CLIENT_PATH),
        ):
            result = await handler(request=request)

        body = json.loads(result.body)
        assert body["fresh"] is True
        mock_client.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_redis_connection_error_falls_through(self):
        """ConnectionError causes graceful fallback to direct execution."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=ConnectionError("refused"))

        @cache(expire=60)
        async def handler(request: Request):
            return JSONResponse({"fallback": True})

        request = _make_request()

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=mock_client)),
            patch(_RESET_CLIENT_PATH) as mock_reset,
        ):
            result = await handler(request=request)

        body = json.loads(result.body)
        assert body["fallback"] is True
        mock_reset.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_request_in_args_is_noop(self):
        """Without a Request argument, the decorator skips caching."""
        call_count = 0

        @cache(expire=60)
        async def handler():
            nonlocal call_count
            call_count += 1
            return JSONResponse({"ok": True})

        with patch(_SETTINGS_PATH, _mock_settings()):
            await handler()
            await handler()

        assert call_count == 2

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        """Wrapper preserves the original function name."""

        @cache(expire=60)
        async def my_cached_route(request: Request):
            return JSONResponse({"ok": True})

        assert my_cached_route.__name__ == "my_cached_route"

    @pytest.mark.asyncio
    async def test_sync_handler(self):
        """Works with synchronous route handlers."""

        @cache(expire=60)
        def handler(request: Request):
            return JSONResponse({"sync": True})

        request = _make_request()

        with patch(_SETTINGS_PATH, _mock_settings(debug=True)):
            result = await handler(request=request)

        body = json.loads(result.body)
        assert body["sync"] is True
