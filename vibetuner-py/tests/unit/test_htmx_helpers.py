# ruff: noqa: S101
"""Tests for htmx request detection and response header helpers."""

import json

from starlette.requests import Request
from starlette.responses import HTMLResponse
from vibetuner.htmx import (
    HtmxDetails,
    hx_location,
    hx_push_url,
    hx_redirect,
    hx_refresh,
    hx_replace_url,
    hx_reswap,
    hx_retarget,
    hx_trigger,
)


def _request(headers: dict[str, str]) -> Request:
    raw = [(key.lower().encode(), value.encode()) for key, value in headers.items()]
    return Request({"type": "http", "headers": raw})


class TestHtmxDetails:
    def test_bool_true_for_htmx_request(self):
        assert bool(HtmxDetails(_request({"HX-Request": "true"})))

    def test_bool_false_without_header(self):
        assert not bool(HtmxDetails(_request({})))

    def test_source_reads_hx_source(self):
        details = HtmxDetails(_request({"HX-Source": "button#save"}))
        assert details.source == "button#save"

    def test_request_type(self):
        assert (
            HtmxDetails(_request({"HX-Request-Type": "partial"})).request_type
            == "partial"
        )

    def test_target_boosted_and_current_url(self):
        details = HtmxDetails(
            _request(
                {
                    "HX-Target": "div#main",
                    "HX-Boosted": "true",
                    "HX-Current-URL": "/dashboard",
                }
            )
        )
        assert details.target == "div#main"
        assert details.boosted is True
        assert details.current_url == "/dashboard"

    def test_prompt(self):
        assert HtmxDetails(_request({"HX-Prompt": "Bob"})).prompt == "Bob"

    def test_uri_autoencoded_value_is_decoded(self):
        details = HtmxDetails(
            _request(
                {
                    "HX-Current-URL": "%2Ffoo%20bar",
                    "HX-Current-URL-URI-AutoEncoded": "true",
                }
            )
        )
        assert details.current_url == "/foo bar"

    def test_no_legacy_htmx2_request_attributes(self):
        details = HtmxDetails(_request({"HX-Request": "true"}))
        assert not hasattr(details, "trigger")
        assert not hasattr(details, "trigger_name")


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
