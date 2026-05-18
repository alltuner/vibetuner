# ABOUTME: Integration tests for LangPrefixMiddleware / LocaleMiddleware ordering
# ABOUTME: Validates the fix for #1861 where URL-prefix locale selector ran before lang_prefix was set
# ruff: noqa: S101

"""Tests that the URL-prefix locale selector observes the stripped prefix.

These tests compose ``LangPrefixMiddleware`` together with
``starlette_babel.LocaleMiddleware`` in the same order used by the framework
and verify that a request to ``/es/`` is detected as locale ``es`` with the
expected ``content-language`` header and ``scope["state"]["language"]``.

A second test inspects the live ``middlewares`` list from
``vibetuner.frontend.middleware`` to assert that ``LangPrefixMiddleware``
appears before ``LocaleMiddleware`` (so the prefix is in scope state by the
time the locale selector runs).

A local copy of the prefix middleware and selector is used for the composed
stack to avoid importing ``vibetuner.frontend.middleware`` indirectly through
fixtures that would touch the unrelated app-bootstrap surface. This mirrors
the approach in ``test_lang_prefix_middleware.py`` and
``test_locale_selector_fn.py``.
"""

import pytest
from starlette.requests import HTTPConnection
from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette_babel import LocaleMiddleware


def locale_selector(conn: HTTPConnection) -> str | None:
    """Mirror of ``vibetuner.frontend.middleware.locale_selector``."""
    return conn.scope.get("state", {}).get("lang_prefix")


class LangPrefixMiddleware:
    """Test copy of ``vibetuner.frontend.middleware.LangPrefixMiddleware``."""

    BYPASS_PREFIXES = ("/static/", "/health/", "/debug/", "/hot-reload")

    def __init__(self, app: ASGIApp, supported_languages: set[str]) -> None:
        self.app = app
        self.supported_languages = supported_languages

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if any(path.startswith(p) for p in self.BYPASS_PREFIXES):
            await self.app(scope, receive, send)
            return

        parts = path.strip("/").split("/", 1)
        if parts and len(parts[0]) == 2 and parts[0].isalpha() and parts[0].islower():
            lang_code = parts[0]
            if lang_code in self.supported_languages:
                if len(parts) == 1 or parts[1] == "":
                    if not path.endswith("/"):
                        await self._redirect(scope, receive, send, f"/{lang_code}/")
                        return

                new_path = "/" + parts[1] if len(parts) > 1 else "/"
                if "state" not in scope:
                    scope = {**scope, "state": {}}
                else:
                    scope = {**scope, "state": {**scope["state"]}}
                scope["path"] = new_path
                scope["state"]["lang_prefix"] = lang_code
                scope["state"]["original_path"] = path
            else:
                response = StarletteResponse(status_code=404, content="Not Found")
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    async def _redirect(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        location: str,
    ) -> None:
        response = StarletteResponse(status_code=302, headers={"Location": location})
        await response(scope, receive, send)


async def _run_stack(
    path: str,
    supported_languages: set[str],
    default_locale: str = "en",
) -> tuple[dict, list[dict]]:
    """Send an ASGI request through LangPrefix -> Locale -> terminal app.

    Returns the final scope seen by the terminal app and the ASGI messages
    sent downstream (so callers can inspect response headers).
    """

    final_scope: dict | None = None
    sent: list[dict] = []

    async def terminal(scope: Scope, receive: Receive, send: Send) -> None:
        nonlocal final_scope
        final_scope = scope
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"OK"})

    locale_app: ASGIApp = LocaleMiddleware(
        terminal,
        locales=list(supported_languages),
        default_locale=default_locale,
        selectors=[locale_selector],
    )
    stack: ASGIApp = LangPrefixMiddleware(
        locale_app, supported_languages=supported_languages
    )

    async def receive() -> dict:
        return {"type": "http.request", "body": b""}

    async def send(message: dict) -> None:
        sent.append(message)

    scope: Scope = {
        "type": "http",
        "path": path,
        "query_string": b"",
        "headers": [],
    }
    await stack(scope, receive, send)
    return final_scope or {}, sent


class TestMiddlewareStackOrdering:
    """Direct check that ``middlewares`` lists LangPrefix before LocaleMiddleware.

    Middleware listed earlier in the Starlette stack wraps middleware listed
    later, so earlier entries run first on the request path. The locale
    selector relies on ``state["lang_prefix"]`` being populated, which means
    LangPrefixMiddleware MUST appear before LocaleMiddleware in the list.
    """

    def test_lang_prefix_precedes_locale(self) -> None:
        from starlette_babel import LocaleMiddleware as FrameworkLocale
        from vibetuner.frontend.middleware import (
            LangPrefixMiddleware as FrameworkLangPrefix,
            middlewares,
        )

        classes = [mw.cls for mw in middlewares]
        assert FrameworkLangPrefix in classes
        assert FrameworkLocale in classes
        assert classes.index(FrameworkLangPrefix) < classes.index(FrameworkLocale), (
            "LangPrefixMiddleware must appear before LocaleMiddleware so the "
            "url_prefix locale selector observes state['lang_prefix']."
        )


class TestLangPrefixBeforeLocaleMiddleware:
    """End-to-end ordering checks for the fix to issue #1861."""

    SUPPORTED = {"en", "es", "ca"}

    @pytest.mark.asyncio
    async def test_es_prefix_yields_es_locale(self) -> None:
        scope, sent = await _run_stack("/es/", self.SUPPORTED)

        assert scope["state"]["lang_prefix"] == "es"
        assert scope["state"]["language"] == "es"
        assert scope["path"] == "/"

        start = next(m for m in sent if m["type"] == "http.response.start")
        headers = dict(start["headers"])
        assert headers.get(b"content-language") == b"es"

    @pytest.mark.asyncio
    async def test_nested_prefixed_path_yields_prefix_locale(self) -> None:
        scope, sent = await _run_stack("/ca/dashboard", self.SUPPORTED)

        assert scope["state"]["lang_prefix"] == "ca"
        assert scope["state"]["language"] == "ca"
        assert scope["path"] == "/dashboard"

        start = next(m for m in sent if m["type"] == "http.response.start")
        headers = dict(start["headers"])
        assert headers.get(b"content-language") == b"ca"

    @pytest.mark.asyncio
    async def test_unprefixed_path_falls_back_to_default(self) -> None:
        scope, sent = await _run_stack(
            "/dashboard", self.SUPPORTED, default_locale="en"
        )

        assert "lang_prefix" not in scope.get("state", {})
        assert scope["state"]["language"] == "en"
        assert scope["path"] == "/dashboard"

        start = next(m for m in sent if m["type"] == "http.response.start")
        headers = dict(start["headers"])
        assert headers.get(b"content-language") == b"en"
