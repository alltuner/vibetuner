# ruff: noqa: S101
"""Tests for HTMX response header helpers."""

import json

from starlette.responses import HTMLResponse
from vibetuner.htmx import (
    hx_location,
    hx_push_url,
    hx_redirect,
    hx_refresh,
    hx_replace_url,
    hx_reswap,
    hx_retarget,
    hx_trigger,
    hx_trigger_after_settle,
    hx_trigger_after_swap,
)


class TestHxRedirect:
    def test_sets_header(self):
        result = hx_redirect("/items/123")
        assert result.headers["HX-Redirect"] == "/items/123"
        assert isinstance(result, HTMLResponse)

    def test_empty_body(self):
        result = hx_redirect("/items")
        assert result.body == b""


class TestHxLocation:
    def test_simple_path(self):
        result = hx_location("/items")
        assert result.headers["HX-Location"] == "/items"

    def test_with_target_and_swap(self):
        result = hx_location("/items", target="#main", swap="innerHTML")
        parsed = json.loads(result.headers["HX-Location"])
        assert parsed["path"] == "/items"
        assert parsed["target"] == "#main"
        assert parsed["swap"] == "innerHTML"

    def test_with_values(self):
        result = hx_location("/search", values={"q": "test"})
        parsed = json.loads(result.headers["HX-Location"])
        assert parsed["values"] == {"q": "test"}


class TestHxTrigger:
    def test_simple_event_name(self):
        response = HTMLResponse("<html>ok</html>")
        hx_trigger(response, "itemCreated")
        assert response.headers["HX-Trigger"] == "itemCreated"

    def test_event_with_detail(self):
        response = HTMLResponse("<html>ok</html>")
        hx_trigger(response, "itemCreated", {"id": "123"})
        parsed = json.loads(response.headers["HX-Trigger"])
        assert parsed == {"itemCreated": {"id": "123"}}

    def test_dict_of_events(self):
        response = HTMLResponse("<html>ok</html>")
        hx_trigger(response, {"showToast": {"message": "Saved!"}, "refreshList": {}})
        parsed = json.loads(response.headers["HX-Trigger"])
        assert parsed["showToast"]["message"] == "Saved!"
        assert parsed["refreshList"] == {}

    def test_returns_same_response(self):
        response = HTMLResponse("<html>ok</html>")
        result = hx_trigger(response, "test")
        assert result is response


class TestHxTriggerAfterSettle:
    def test_sets_header(self):
        response = HTMLResponse("<html>ok</html>")
        hx_trigger_after_settle(response, "settled")
        assert response.headers["HX-Trigger-After-Settle"] == "settled"

    def test_with_detail(self):
        response = HTMLResponse("<html>ok</html>")
        hx_trigger_after_settle(response, "done", {"count": 5})
        parsed = json.loads(response.headers["HX-Trigger-After-Settle"])
        assert parsed == {"done": {"count": 5}}


class TestHxTriggerAfterSwap:
    def test_sets_header(self):
        response = HTMLResponse("<html>ok</html>")
        hx_trigger_after_swap(response, "swapped")
        assert response.headers["HX-Trigger-After-Swap"] == "swapped"


class TestHxPushUrl:
    def test_sets_header(self):
        response = HTMLResponse("<html>ok</html>")
        hx_push_url(response, "/items?page=2")
        assert response.headers["HX-Push-Url"] == "/items?page=2"

    def test_returns_same_response(self):
        response = HTMLResponse("<html>ok</html>")
        result = hx_push_url(response, "/items")
        assert result is response


class TestHxReplaceUrl:
    def test_sets_header(self):
        response = HTMLResponse("<html>ok</html>")
        hx_replace_url(response, "/items?page=2")
        assert response.headers["HX-Replace-Url"] == "/items?page=2"


class TestHxReswap:
    def test_sets_header(self):
        response = HTMLResponse("<html>ok</html>")
        hx_reswap(response, "outerHTML")
        assert response.headers["HX-Reswap"] == "outerHTML"


class TestHxRetarget:
    def test_sets_header(self):
        response = HTMLResponse("<html>ok</html>")
        hx_retarget(response, "#error-container")
        assert response.headers["HX-Retarget"] == "#error-container"


class TestHxRefresh:
    def test_sets_header(self):
        response = HTMLResponse("<html>ok</html>")
        hx_refresh(response)
        assert response.headers["HX-Refresh"] == "true"

    def test_returns_same_response(self):
        response = HTMLResponse("<html>ok</html>")
        result = hx_refresh(response)
        assert result is response
