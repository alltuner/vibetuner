# ABOUTME: Server-Sent Events helpers for real-time streaming with HTMX.
# ABOUTME: Provides decorator for SSE endpoints, broadcast function, and Redis pub/sub backend.
import asyncio
import json
import re
from collections import deque
from collections.abc import AsyncGenerator, Callable
from contextlib import suppress
from functools import wraps
from typing import Any

from fastapi import APIRouter, Request
from fastapi.sse import EventSourceResponse, format_sse_event

from vibetuner.logging import logger
from vibetuner.rendering import render_template_string


# ────────────────────────────────────────────────────────────────
#  Channel name validation
# ────────────────────────────────────────────────────────────────

_MAX_CHANNEL_LENGTH = 128
_CHANNEL_NAME_RE = re.compile(r"^[a-zA-Z0-9\-:_.]+$")


def _validate_channel_name(channel: str) -> None:
    """Validate an SSE channel name.

    Channel names must be non-empty, at most 128 characters, and contain only
    alphanumeric characters, hyphens, colons, underscores, and dots.

    Raises:
        ValueError: If the channel name is invalid.
    """
    if not channel:
        raise ValueError("Channel name must not be empty")
    if len(channel) > _MAX_CHANNEL_LENGTH:
        raise ValueError(
            f"Channel name exceeds maximum length of {_MAX_CHANNEL_LENGTH} characters"
        )
    if not _CHANNEL_NAME_RE.match(channel):
        raise ValueError(
            "Channel name contains invalid characters. "
            "Allowed: alphanumeric, hyphens, colons, underscores, dots"
        )


# ────────────────────────────────────────────────────────────────
#  Event buffer for Last-Event-ID resumption
# ────────────────────────────────────────────────────────────────


class _EventBuffer:
    """Per-channel ring buffer that stores recent events with monotonic IDs.

    Used for Last-Event-ID resumption: when a client reconnects, events
    after the last seen ID are replayed before switching to live streaming.
    """

    __slots__ = ("_buf", "_next_id")

    def __init__(self, maxlen: int = 100) -> None:
        self._buf: deque[tuple[int, dict[str, str]]] = deque(maxlen=maxlen)
        self._next_id = 1

    def append(self, payload: dict[str, str]) -> int:
        """Store an event and return its assigned ID."""
        event_id = self._next_id
        self._next_id += 1
        self._buf.append((event_id, payload))
        return event_id

    def events_after(self, last_id: int) -> list[tuple[int, dict[str, str]]]:
        """Return all buffered events with ID > last_id."""
        return [(eid, p) for eid, p in self._buf if eid > last_id]


# ────────────────────────────────────────────────────────────────
#  Wire-format encoding
# ────────────────────────────────────────────────────────────────


def _format_event(
    payload: dict[str, str], *, event_id: str | None = None
) -> bytes:
    """Encode an SSE payload dict into wire-format bytes.

    Wraps fastapi.sse.format_sse_event for internal use.
    """
    return format_sse_event(
        data_str=payload.get("data"),
        event=payload.get("event"),
        id=event_id,
        comment=payload.get("comment"),
    )


# ────────────────────────────────────────────────────────────────
#  In-process connection registry
# ────────────────────────────────────────────────────────────────

_channels: dict[str, set[asyncio.Queue]] = {}
_channel_buffers: dict[str, _EventBuffer] = {}


def _subscribe(channel: str) -> asyncio.Queue:
    """Add a new subscriber queue to a channel."""
    queue: asyncio.Queue = asyncio.Queue()
    _channels.setdefault(channel, set()).add(queue)
    return queue


def _unsubscribe(channel: str, queue: asyncio.Queue) -> None:
    """Remove a subscriber queue from a channel."""
    if channel in _channels:
        _channels[channel].discard(queue)
        if not _channels[channel]:
            del _channels[channel]


def _dispatch_local(channel: str, payload: dict[str, str]) -> int | None:
    """Dispatch a payload to all local subscribers of a channel.

    Returns the event ID if the channel has a buffer, else None.
    """
    event_id: int | None = None
    if channel in _channel_buffers:
        event_id = _channel_buffers[channel].append(payload)

    if channel in _channels:
        for q in list(_channels[channel]):
            with suppress(asyncio.QueueFull):
                q.put_nowait((event_id, payload))

    return event_id


# ────────────────────────────────────────────────────────────────
#  Redis pub/sub bridge (optional, for multi-worker)
# ────────────────────────────────────────────────────────────────

_redis_listener_task: asyncio.Task | None = None
_redis_publish_client = None


def _parse_redis_message(message: dict, prefix: str) -> tuple[str, dict] | None:
    """Parse a Redis pub/sub message into (channel, payload) or None.

    Returns None and logs a warning for malformed messages (invalid JSON,
    missing keys, wrong types) instead of raising.
    """
    if message["type"] != "pmessage":
        return None

    redis_channel = message["channel"]
    if isinstance(redis_channel, bytes):
        redis_channel = redis_channel.decode()
    channel = redis_channel.removeprefix(prefix)

    data = message["data"]
    if isinstance(data, bytes):
        data = data.decode()

    try:
        payload = json.loads(data)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("SSE Redis message has invalid JSON on {}: {}", channel, exc)
        return None

    if not isinstance(payload, dict):
        logger.warning(
            "SSE Redis message is not a dict on {}: {!r}",
            channel,
            type(payload).__name__,
        )
        return None

    if "event" not in payload and "data" not in payload:
        logger.warning(
            "SSE Redis message missing 'event' and 'data' keys on {}", channel
        )
        return None

    return channel, {
        "event": payload.get("event", "message"),
        "data": payload.get("data", ""),
    }


async def _redis_listen_loop(pubsub, client, prefix: str) -> None:
    """Run the Redis pub/sub listen loop, dispatching to local subscribers."""
    try:
        async for message in pubsub.listen():
            parsed = _parse_redis_message(message, prefix)
            if parsed is not None:
                _dispatch_local(*parsed)
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.punsubscribe()
        await client.aclose()


async def _start_redis_listener() -> None:
    """Start a background task that relays Redis pub/sub messages to local queues."""
    global _redis_listener_task
    if _redis_listener_task is not None:
        return

    try:
        from vibetuner.config import settings
        from vibetuner.redis import create_redis_client

        client = create_redis_client()
        if client is None:
            return

        pubsub = client.pubsub()
        prefix = f"{settings.redis_key_prefix}sse:"
        await pubsub.psubscribe(f"{prefix}*")

        _redis_listener_task = asyncio.create_task(
            _redis_listen_loop(pubsub, client, prefix)
        )
        logger.debug("SSE Redis pub/sub listener started")
    except ImportError:
        logger.debug("Redis not available, SSE broadcasting is local-only")
    except Exception as e:
        logger.warning("Failed to start SSE Redis listener: {}", e)


async def _stop_redis_listener() -> None:
    """Cancel the Redis listener task and close the publish client."""
    global _redis_listener_task
    if _redis_listener_task is not None:
        _redis_listener_task.cancel()
        with suppress(asyncio.CancelledError):
            await _redis_listener_task
        _redis_listener_task = None
    await _close_redis_publish_client()


async def _get_redis_publish_client():
    """Get the shared Redis client for publishing."""
    global _redis_publish_client
    if _redis_publish_client is None:
        from vibetuner.redis import get_redis_client

        _redis_publish_client = await get_redis_client()
    return _redis_publish_client


async def _close_redis_publish_client() -> None:
    """Release the local reference to the shared Redis publish client."""
    global _redis_publish_client
    # Don't close the shared client — just drop the local reference.
    _redis_publish_client = None


async def _publish_to_redis(channel: str, payload: dict[str, str]) -> None:
    """Publish a payload to Redis for multi-worker broadcasting (best-effort)."""
    global _redis_publish_client
    try:
        client = await _get_redis_publish_client()
        if client is None:
            return

        from vibetuner.config import settings

        redis_channel = f"{settings.redis_key_prefix}sse:{channel}"
        await client.publish(redis_channel, json.dumps(payload))
    except (ConnectionError, OSError):
        logger.debug(
            "Redis SSE publish failed due to connection error, resetting client"
        )
        from vibetuner.redis import reset_redis_client

        _redis_publish_client = None
        reset_redis_client()
    except Exception:
        logger.debug("Redis SSE publish failed (local dispatch still succeeded)")


# ────────────────────────────────────────────────────────────────
#  Public API: broadcast()
# ────────────────────────────────────────────────────────────────


async def broadcast(
    channel: str,
    event: str = "message",
    *,
    data: str = "",
    template: str | None = None,
    request: Request | None = None,
    ctx: dict[str, Any] | None = None,
) -> None:
    """Broadcast an SSE event to all subscribers of a channel.

    Can broadcast raw data or render a Jinja2 template first.

    Args:
        channel: Channel name to broadcast to.
        event: SSE event name (default: "message").
        data: Raw string data to send. Ignored if template is set.
        template: Optional Jinja2 template path to render as the data payload.
        request: Required when using template rendering.
        ctx: Template context dict (used with template).

    Example:
        # Raw data
        await broadcast("notifications", "update", data="<div>New item!</div>")

        # With template rendering
        await broadcast(
            "feed",
            "new-post",
            template="partials/post.html.jinja",
            request=request,
            ctx={"post": post},
        )
    """
    _validate_channel_name(channel)

    if template is not None:
        if request is None:
            raise ValueError("request is required when broadcasting with a template")
        data = render_template_string(template, request, ctx)

    payload = {"event": event, "data": data}
    _dispatch_local(channel, payload)
    await _publish_to_redis(channel, payload)


# ────────────────────────────────────────────────────────────────
#  Public API: sse_endpoint() decorator
# ────────────────────────────────────────────────────────────────


async def _stream_from_generator(
    result: AsyncGenerator, template: str | None, request: Request
) -> AsyncGenerator[bytes, None]:
    """Yield SSE wire-format bytes from a user-provided async generator."""
    async for event in result:
        if isinstance(event, dict):
            data = event.get("data", "")
            if template and not data:
                data = render_template_string(template, request, event.get("ctx"))
                event = {**event, "data": data}
            yield _format_event(event)
        else:
            yield _format_event({"data": str(event)})


async def _stream_from_channel(
    ch: str, *, last_event_id: int | None = None
) -> AsyncGenerator[bytes, None]:
    """Subscribe to a channel and yield SSE wire-format bytes with keepalive.

    If last_event_id is set and the channel has a buffer, replays missed
    events before switching to live streaming.
    """
    # Replay buffered events if resuming
    if last_event_id is not None and ch in _channel_buffers:
        for eid, payload in _channel_buffers[ch].events_after(last_event_id):
            yield _format_event(payload, event_id=str(eid))

    queue = _subscribe(ch)
    try:
        while True:
            try:
                event_id, payload = await asyncio.wait_for(
                    queue.get(), timeout=30
                )
                yield _format_event(
                    payload,
                    event_id=str(event_id) if event_id is not None else None,
                )
            except asyncio.TimeoutError:
                yield _format_event({"comment": "keepalive"})
    except asyncio.CancelledError:
        pass
    finally:
        _unsubscribe(ch, queue)


async def _resolve_channel_or_generator(
    func: Callable, kwargs: dict, static_channel: str | None
) -> tuple[str | None, AsyncGenerator | None]:
    """Call the decorated function and determine if it returns a channel name or generator."""
    result = func(**kwargs)
    if asyncio.iscoroutine(result):
        result = await result

    if isinstance(result, str):
        return result, None
    if hasattr(result, "__aiter__"):
        return None, result
    return static_channel, None


def _parse_last_event_id(request: Request) -> int | None:
    """Extract and parse the Last-Event-ID header from a request.

    Returns the integer event ID, or None if the header is absent or not a
    valid integer.
    """
    raw = request.headers.get("last-event-id")
    if raw is not None:
        try:
            return int(raw)
        except (ValueError, TypeError):
            pass
    return None


def sse_endpoint(
    path: str,
    *,
    channel: str | None = None,
    template: str | None = None,
    router: APIRouter | None = None,
    name: str | None = None,
    buffer_size: int | None = None,
) -> Callable:
    """Decorator that creates an SSE endpoint with automatic connection management.

    The decorated function is a *generator* that yields SSE events. Or, if
    ``channel`` is provided, the endpoint subscribes to that channel and streams
    events automatically (the decorated function is used to compute the channel
    name dynamically if it returns a string).

    Args:
        path: URL path for the SSE endpoint, **relative to the router prefix**
            (same as ``@router.get()``). For example, if ``router`` has
            ``prefix="/live"`` and you pass ``path="/events"``, the final URL
            will be ``/live/events``.
        channel: Static channel name to subscribe to. If the decorated function
            returns a string, it is used as the channel name instead.
        template: Default template for rendering events on this endpoint.
        router: APIRouter to register the route on. If None, a new one is created.
        name: Optional route name.
        buffer_size: If set, enables a ring buffer of this size for the channel.
            When a client reconnects with a ``Last-Event-ID`` header, missed
            events are replayed before switching to live streaming.

    Returns:
        Decorator that wraps a function into an SSE endpoint.

    Example:
        router = APIRouter()

        # Channel-based: auto-subscribe to "notifications"
        @sse_endpoint("/events/notifications", channel="notifications", router=router)
        async def notifications_stream(request: Request):
            pass  # channel kwarg handles everything

        # Dynamic channel based on path params
        @sse_endpoint("/events/room/{room_id}", router=router)
        async def room_stream(request: Request, room_id: str):
            return f"room:{room_id}"  # return channel name

        # Generator-based: full control
        @sse_endpoint("/events/custom", router=router)
        async def custom_stream(request: Request):
            while True:
                yield {"event": "tick", "data": "ping"}
                await asyncio.sleep(5)
    """

    def decorator(func: Callable) -> Callable:
        # Register buffer for static channels at decoration time
        if buffer_size is not None and channel is not None:
            _channel_buffers[channel] = _EventBuffer(maxlen=buffer_size)

        @wraps(func)
        async def endpoint(**kwargs):
            request: Request = kwargs["request"]
            await _start_redis_listener()

            ch, gen = await _resolve_channel_or_generator(func, kwargs, channel)

            if gen is not None:
                return EventSourceResponse(
                    _stream_from_generator(gen, template, request)
                )

            if ch is None:
                raise ValueError(
                    "sse_endpoint requires either a 'channel' argument, "
                    "the decorated function to return a channel name, "
                    "or the function to be an async generator."
                )

            _validate_channel_name(ch)

            # Register buffer for dynamic channels on first connection
            if buffer_size is not None and ch not in _channel_buffers:
                _channel_buffers[ch] = _EventBuffer(maxlen=buffer_size)

            return EventSourceResponse(
                _stream_from_channel(
                    ch, last_event_id=_parse_last_event_id(request)
                )
            )

        if router is not None:
            if router.prefix and path.startswith(router.prefix):
                logger.warning(
                    f"sse_endpoint path '{path}' starts with router prefix "
                    f"'{router.prefix}' — this will produce a doubled path "
                    f"'{router.prefix}{path}'. Use a relative path instead "
                    f"(e.g., '{path[len(router.prefix) :]}')"
                )
            router.add_api_route(path, endpoint, methods=["GET"], name=name)

        return endpoint

    return decorator
