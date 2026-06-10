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
    invalidate,
    invalidate_pattern,
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


def _mock_redis_client():
    """Mock Redis client whose pipeline() queues commands synchronously."""
    client = AsyncMock()
    pipe = MagicMock()
    pipe.execute = AsyncMock()
    client.pipeline = MagicMock(return_value=pipe)
    return client, pipe


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
        mock_client, _ = _mock_redis_client()
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

        mock_client, _ = _mock_redis_client()
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


class TestVaryOn:
    """Test the vary_on parameter for request-dependent cache keying."""

    @pytest.mark.asyncio
    async def test_vary_on_produces_different_keys(self):
        """Different vary_on values produce different cache keys."""
        mock_client, _ = _mock_redis_client()
        mock_client.get = AsyncMock(return_value=None)
        mock_client.set = AsyncMock()

        captured_keys: list[str] = []
        original_build = _build_cache_key

        def spy_build(*args, **kwargs):
            key = original_build(*args, **kwargs)
            captured_keys.append(key)
            return key

        @cache(expire=60, vary_on=lambda r: r.headers.get("x-tenant", ""))
        async def handler(request: Request):
            return JSONResponse({"ok": True})

        req_a = _make_request(headers={"x-tenant": "tenant-a"})
        req_b = _make_request(headers={"x-tenant": "tenant-b"})

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=mock_client)),
            patch(_RESET_CLIENT_PATH),
            patch("vibetuner.cache._build_cache_key", side_effect=spy_build),
        ):
            await handler(request=req_a)
            await handler(request=req_b)

        assert len(captured_keys) == 2
        assert captured_keys[0] != captured_keys[1]

    @pytest.mark.asyncio
    async def test_vary_on_same_value_hits_cache(self):
        """Same vary_on value reuses the cached response."""
        cached_data = json.dumps(
            {"type": "json", "body": '{"cached": true}', "status": 200}
        ).encode()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=cached_data)
        call_count = 0

        @cache(expire=60, vary_on=lambda r: r.headers.get("x-tenant", ""))
        async def handler(request: Request):
            nonlocal call_count
            call_count += 1
            return JSONResponse({"cached": False})

        req = _make_request(headers={"x-tenant": "tenant-a"})

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=mock_client)),
            patch(_RESET_CLIENT_PATH),
        ):
            await handler(request=req)
            await handler(request=req)

        assert call_count == 0  # Both served from cache

    @pytest.mark.asyncio
    async def test_vary_on_none_uses_path_only(self):
        """When vary_on is None (default), cache key uses path only."""
        key = _build_cache_key("p:", "/test", "", None)
        key_explicit_none = _build_cache_key("p:", "/test", "", None)
        assert key == key_explicit_none

    @pytest.mark.asyncio
    async def test_vary_on_empty_string_same_as_no_vary(self):
        """A vary_on that returns empty string produces same key as no vary_on."""
        key_no_vary = _build_cache_key("p:", "/test", "", None)
        key_empty = _build_cache_key("p:", "/test", "", "")
        assert key_no_vary == key_empty

    @pytest.mark.asyncio
    async def test_vary_on_value_included_in_key(self):
        """The vary_on value is reflected in the cache key."""
        key_a = _build_cache_key("p:", "/test", "", "user-123")
        key_b = _build_cache_key("p:", "/test", "", "user-456")
        assert key_a != key_b

    @pytest.mark.asyncio
    async def test_vary_on_with_debug_mode_skips_caching(self):
        """vary_on is irrelevant when debug mode disables caching."""
        call_count = 0

        @cache(expire=60, vary_on=lambda r: "anything")
        async def handler(request: Request):
            nonlocal call_count
            call_count += 1
            return JSONResponse({"count": call_count})

        request = _make_request()

        with patch(_SETTINGS_PATH, _mock_settings(debug=True)):
            await handler(request=request)
            await handler(request=request)

        assert call_count == 2


class TestInvalidate:
    """Test exact-key invalidation, including vary'd variants."""

    @pytest.mark.asyncio
    async def test_invalidate_deletes_path_key(self):
        client, _ = _mock_redis_client()
        client.delete = AsyncMock(return_value=1)

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            result = await invalidate("/api/stats")

        assert result is True
        expected = _build_cache_key("test:", "/api/stats", "")
        client.delete.assert_awaited_once_with(expected)

    @pytest.mark.asyncio
    async def test_invalidate_with_vary_targets_varied_key(self):
        """invalidate(path, vary=...) deletes the key written for that variant."""
        client, _ = _mock_redis_client()
        client.delete = AsyncMock(return_value=1)

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            result = await invalidate("/dashboard", vary="user-123")

        assert result is True
        expected = _build_cache_key("test:", "/dashboard", "", "user-123")
        client.delete.assert_awaited_once_with(expected)

    @pytest.mark.asyncio
    async def test_invalidate_with_query_and_vary(self):
        client, _ = _mock_redis_client()
        client.delete = AsyncMock(return_value=0)

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            result = await invalidate(
                "/reports", query_params="page=1", vary="tenant-a"
            )

        assert result is False
        expected = _build_cache_key("test:", "/reports", "page=1", "tenant-a")
        client.delete.assert_awaited_once_with(expected)


class TestKeyRegistry:
    """Cache writes register their key in a per-path Redis set."""

    @pytest.mark.asyncio
    async def test_write_registers_key_with_ttl_floor(self):
        """A cache write SADDs the key and bumps registry TTLs via NX then GT."""
        client, pipe = _mock_redis_client()
        client.get = AsyncMock(return_value=None)
        client.set = AsyncMock()

        @cache(expire=120)
        async def handler(request: Request):
            return JSONResponse({"ok": True})

        request = _make_request(path="/api/stats")

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
            patch(_RESET_CLIENT_PATH),
        ):
            await handler(request=request)

        cache_key = _build_cache_key("test:", "/api/stats", "")
        registry = "test:cache-index:/api/stats"
        paths_index = "test:cache-paths"

        pipe.sadd.assert_any_call(registry, cache_key)
        pipe.sadd.assert_any_call(paths_index, "/api/stats")
        pipe.expire.assert_any_call(registry, 120, nx=True)
        pipe.expire.assert_any_call(registry, 120, gt=True)
        pipe.expire.assert_any_call(paths_index, 120, nx=True)
        pipe.expire.assert_any_call(paths_index, 120, gt=True)
        pipe.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_varied_writes_register_in_same_path_registry(self):
        """Vary'd variants of a path land in the same per-path registry set."""
        client, pipe = _mock_redis_client()
        client.get = AsyncMock(return_value=None)
        client.set = AsyncMock()

        @cache(expire=60, vary_on=lambda r: r.headers.get("x-tenant", ""))
        async def handler(request: Request):
            return JSONResponse({"ok": True})

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
            patch(_RESET_CLIENT_PATH),
        ):
            await handler(request=_make_request(headers={"x-tenant": "a"}))
            await handler(request=_make_request(headers={"x-tenant": "b"}))

        registry = "test:cache-index:/test"
        key_a = _build_cache_key("test:", "/test", "", "a")
        key_b = _build_cache_key("test:", "/test", "", "b")
        pipe.sadd.assert_any_call(registry, key_a)
        pipe.sadd.assert_any_call(registry, key_b)

    @pytest.mark.asyncio
    async def test_registry_failure_does_not_rerun_handler(self):
        """A failed registry write must not re-execute the handler."""
        client, pipe = _mock_redis_client()
        client.get = AsyncMock(return_value=None)
        client.set = AsyncMock()
        pipe.execute = AsyncMock(side_effect=ConnectionError("refused"))
        call_count = 0

        @cache(expire=60)
        async def handler(request: Request):
            nonlocal call_count
            call_count += 1
            return JSONResponse({"ok": True})

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
            patch(_RESET_CLIENT_PATH),
        ):
            result = await handler(request=_make_request())

        assert call_count == 1
        assert json.loads(result.body) == {"ok": True}


class TestInvalidatePattern:
    """Pattern invalidation works off the key registry, never a keyspace SCAN."""

    @staticmethod
    def _client_with_sets(sets: dict[str, set]):
        client, _ = _mock_redis_client()

        async def smembers(key):
            return sets.get(key, set())

        client.smembers = AsyncMock(side_effect=smembers)
        client.unlink = AsyncMock(side_effect=lambda *keys: len(keys))
        client.srem = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_exact_path_deletes_all_variants(self):
        """A bare path removes every registered variant plus the registry set."""
        key_plain = _build_cache_key("test:", "/dashboard", "")
        key_u1 = _build_cache_key("test:", "/dashboard", "", "u1")
        key_u2 = _build_cache_key("test:", "/dashboard", "", "u2")
        client = self._client_with_sets(
            {"test:cache-index:/dashboard": {key_plain, key_u1, key_u2}}
        )

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            deleted = await invalidate_pattern("/dashboard")

        assert deleted == 3
        unlinked = {k for call_ in client.unlink.await_args_list for k in call_.args}
        assert {key_plain, key_u1, key_u2} <= unlinked
        assert "test:cache-index:/dashboard" in unlinked
        client.srem.assert_awaited_once_with("test:cache-paths", "/dashboard")
        client.scan_iter.assert_not_called()

    @pytest.mark.asyncio
    async def test_glob_pattern_deletes_matching_variants(self):
        """A glob pattern matches registered keys across paths, without SCAN."""
        key_stats = _build_cache_key("test:", "/api/stats", "page=1")
        key_users = _build_cache_key("test:", "/api/users", "", "u1")
        key_home = _build_cache_key("test:", "/home", "")
        client = self._client_with_sets(
            {
                "test:cache-paths": {"/api/stats", "/api/users", "/home"},
                "test:cache-index:/api/stats": {key_stats},
                "test:cache-index:/api/users": {key_users},
                "test:cache-index:/home": {key_home},
            }
        )

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            deleted = await invalidate_pattern("/api/*")

        assert deleted == 2
        unlinked = {k for call_ in client.unlink.await_args_list for k in call_.args}
        assert key_stats in unlinked
        assert key_users in unlinked
        assert key_home not in unlinked
        client.scan_iter.assert_not_called()

    @pytest.mark.asyncio
    async def test_glob_partial_match_keeps_registry(self):
        """Unmatched variants stay registered; matched ones are SREM'd."""
        key_p1 = _build_cache_key("test:", "/api/stats", "page=1")
        key_bare = _build_cache_key("test:", "/api/stats", "")
        client = self._client_with_sets(
            {
                "test:cache-paths": {"/api/stats"},
                "test:cache-index:/api/stats": {key_p1, key_bare},
            }
        )

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            deleted = await invalidate_pattern("/api/stats[?]page=*")

        assert deleted == 1
        unlinked = {k for call_ in client.unlink.await_args_list for k in call_.args}
        assert key_p1 in unlinked
        assert key_bare not in unlinked
        assert "test:cache-index:/api/stats" not in unlinked
        client.srem.assert_awaited_once_with("test:cache-index:/api/stats", key_p1)

    @pytest.mark.asyncio
    async def test_bytes_members_are_decoded(self):
        """Registry members stored as bytes are handled transparently."""
        key = _build_cache_key("test:", "/api/stats", "")
        client = self._client_with_sets({"test:cache-index:/api/stats": {key.encode()}})

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            deleted = await invalidate_pattern("/api/stats")

        assert deleted == 1
        unlinked = {k for call_ in client.unlink.await_args_list for k in call_.args}
        assert key in unlinked

    @pytest.mark.asyncio
    async def test_no_entries_returns_zero(self):
        client = self._client_with_sets({})

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            assert await invalidate_pattern("/nothing") == 0
            assert await invalidate_pattern("/nothing/*") == 0

    @pytest.mark.asyncio
    async def test_redis_unavailable_returns_zero(self):
        client, _ = _mock_redis_client()
        client.smembers = AsyncMock(side_effect=ConnectionError("refused"))

        with (
            patch(_SETTINGS_PATH, _mock_settings()),
            patch(_GET_CLIENT_PATH, AsyncMock(return_value=client)),
        ):
            assert await invalidate_pattern("/api/*") == 0
