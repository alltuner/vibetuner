# ABOUTME: htmx 4 request detection (HtmxDetails) and response-header helpers.
# ABOUTME: Reduces boilerplate when building interactive htmx flows.
import json
from functools import cached_property
from typing import Any
from urllib.parse import unquote

from starlette.requests import Request
from starlette.responses import HTMLResponse, Response


class HtmxDetails:
    """htmx request metadata read from the ``HX-*`` request headers.

    Wired onto ``request.state.htmx`` by ``HtmxMiddleware``. Truthiness tells
    whether the request originated from htmx::

        if request.state.htmx:
            ...  # htmx-driven request

    Only the headers htmx 4 sends are exposed. The htmx 2 request ``HX-Trigger``
    was renamed to ``HX-Source`` (read it via :attr:`source`) and
    ``HX-Trigger-Name`` was dropped, so neither has an attribute here.
    """

    def __init__(self, request: Request) -> None:
        self.request = request

    def _header(self, name: str) -> str | None:
        value = self.request.headers.get(name) or None
        if value and self.request.headers.get(f"{name}-URI-AutoEncoded") == "true":
            value = unquote(value)
        return value

    def __bool__(self) -> bool:
        return self._header("HX-Request") == "true"

    @cached_property
    def boosted(self) -> bool:
        return self._header("HX-Boosted") == "true"

    @cached_property
    def current_url(self) -> str | None:
        return self._header("HX-Current-URL")

    @cached_property
    def history_restore_request(self) -> bool:
        return self._header("HX-History-Restore-Request") == "true"

    @cached_property
    def prompt(self) -> str | None:
        """User reply captured by the ``hx-prompt`` extension (``HX-Prompt``)."""
        return self._header("HX-Prompt")

    @cached_property
    def target(self) -> str | None:
        """Target element as ``tag#id`` (``HX-Target``)."""
        return self._header("HX-Target")

    @cached_property
    def source(self) -> str | None:
        """Triggering element as ``tag#id`` (``HX-Source``; the htmx 2 request ``HX-Trigger``)."""
        return self._header("HX-Source")

    @cached_property
    def request_type(self) -> str | None:
        """``"full"`` or ``"partial"`` (``HX-Request-Type``)."""
        return self._header("HX-Request-Type")


def hx_redirect(url: str) -> HTMLResponse:
    """Return a response that triggers a full-reload redirect via HTMX.

    Use when the target page has a different ``<head>`` or scripts that
    require a full page load.

    Args:
        url: The URL to redirect to.

    Returns:
        An empty HTMLResponse with the ``HX-Redirect`` header set.

    Example::

        @router.post("/items")
        async def create_item(request: Request):
            item = await Item.insert(...)
            return hx_redirect(f"/items/{item.id}")
    """
    response = HTMLResponse("", status_code=200)
    response.headers["HX-Redirect"] = url
    return response


def hx_location(
    path: str,
    *,
    target: str | None = None,
    swap: str | None = None,
    source: str | None = None,
    event: str | None = None,
    handler: str | None = None,
    values: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    select: str | None = None,
) -> HTMLResponse:
    """Return a response that triggers HTMX navigation without a full reload.

    Uses the ``HX-Location`` header to navigate to a new URL using the HTMX
    swap mechanism, avoiding a full page reload.

    Args:
        path: URL path to navigate to.
        target: CSS selector for the target element.
        swap: Swap strategy (e.g. ``"innerHTML"``, ``"outerHTML"``).
        source: Source element CSS selector.
        event: Event that triggered the request.
        handler: Handler for processing the response.
        values: Values to submit with the request.
        headers: Additional headers to include.
        select: CSS selector to pick content from the response.

    Returns:
        An empty HTMLResponse with the ``HX-Location`` header set.

    Example::

        return hx_location("/items", target="#main", swap="innerHTML")
    """
    opts: dict[str, Any] = {"path": path}
    for key, val in [
        ("target", target),
        ("swap", swap),
        ("source", source),
        ("event", event),
        ("handler", handler),
        ("values", values),
        ("headers", headers),
        ("select", select),
    ]:
        if val is not None:
            opts[key] = val

    response = HTMLResponse("", status_code=200)
    # Simple path-only case uses plain string; complex case uses JSON
    if len(opts) == 1:
        response.headers["HX-Location"] = path
    else:
        response.headers["HX-Location"] = json.dumps(opts)
    return response


def hx_trigger(
    response: Response,
    event: str | dict[str, Any],
    detail: dict[str, Any] | None = None,
) -> Response:
    """Set the ``HX-Trigger`` header on a response.

    Triggers client-side events after the HTMX swap completes.

    Args:
        response: The response to modify.
        event: Event name (str) or dict of ``{event_name: detail}``.
        detail: Optional detail object when ``event`` is a string.

    Returns:
        The same response object with the header set.

    Example::

        response = render_template("items/created.html.jinja", request, ctx)
        hx_trigger(response, "itemCreated", {"id": str(item.id)})
        return response

        # Multiple events
        hx_trigger(response, {"showToast": {"message": "Saved!"}, "refreshList": {}})
    """
    if isinstance(event, dict):
        response.headers["HX-Trigger"] = json.dumps(event)
    elif detail is not None:
        response.headers["HX-Trigger"] = json.dumps({event: detail})
    else:
        response.headers["HX-Trigger"] = event
    return response


def hx_push_url(response: Response, url: str) -> Response:
    """Set the ``HX-Push-Url`` header to update the browser URL and history.

    Args:
        response: The response to modify.
        url: The URL to push into browser history.

    Returns:
        The same response object with the header set.
    """
    response.headers["HX-Push-Url"] = url
    return response


def hx_replace_url(response: Response, url: str) -> Response:
    """Set the ``HX-Replace-Url`` header to replace the current URL without history.

    Args:
        response: The response to modify.
        url: The URL to replace in the address bar (no history entry).

    Returns:
        The same response object with the header set.
    """
    response.headers["HX-Replace-Url"] = url
    return response


def hx_reswap(response: Response, strategy: str) -> Response:
    """Set the ``HX-Reswap`` header to override the swap strategy.

    Args:
        response: The response to modify.
        strategy: Swap strategy (e.g. ``"outerHTML"``, ``"innerHTML"``,
            ``"beforeend"``).

    Returns:
        The same response object with the header set.
    """
    response.headers["HX-Reswap"] = strategy
    return response


def hx_retarget(response: Response, selector: str) -> Response:
    """Set the ``HX-Retarget`` header to override the target element.

    Args:
        response: The response to modify.
        selector: CSS selector for the new target element.

    Returns:
        The same response object with the header set.
    """
    response.headers["HX-Retarget"] = selector
    return response


def hx_refresh(response: Response) -> Response:
    """Set the ``HX-Refresh`` header to force a full page refresh.

    Args:
        response: The response to modify.

    Returns:
        The same response object with the header set.
    """
    response.headers["HX-Refresh"] = "true"
    return response
