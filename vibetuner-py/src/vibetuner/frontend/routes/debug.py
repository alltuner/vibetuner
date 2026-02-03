import asyncio
from collections import deque
from datetime import UTC, datetime
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)
from sse_starlette.sse import EventSourceResponse

from vibetuner.config import settings
from vibetuner.context import ctx
from vibetuner.models import UserModel
from vibetuner.mongo import get_all_models

from ..deps import MAGIC_COOKIE_NAME
from ..templates import render_template


# Claude Code event broadcasting
_claude_events: deque[dict[str, Any]] = deque(maxlen=100)
_claude_subscribers: set[asyncio.Queue] = set()
_shutdown_event: asyncio.Event | None = None


def _get_shutdown_event() -> asyncio.Event:
    """Get or create the shutdown event for the current event loop."""
    global _shutdown_event
    if _shutdown_event is None:
        _shutdown_event = asyncio.Event()
    return _shutdown_event


async def shutdown_sse_connections() -> None:
    """Signal all SSE connections to terminate gracefully."""
    event = _get_shutdown_event()
    event.set()
    await asyncio.sleep(0.1)


def reset_sse_state() -> None:
    """Reset SSE state for dev mode reloads."""
    global _shutdown_event
    _shutdown_event = None


def check_debug_access(request: Request):
    """Check if debug routes should be accessible."""
    # Always allow in development mode
    if ctx.DEBUG:
        return True

    # In production, require magic cookie
    if MAGIC_COOKIE_NAME not in request.cookies:
        raise HTTPException(status_code=404, detail="Not found")
    if request.cookies[MAGIC_COOKIE_NAME] != "granted":
        raise HTTPException(status_code=404, detail="Not found")

    return True


# Unprotected router for token-based debug access
auth_router = APIRouter()


@auth_router.get("/_unlock-debug")
def unlock_debug_access(token: str | None = None):
    """Grant debug access by setting the magic cookie.

    In DEBUG mode, no token is required.
    In production, the token must match DEBUG_ACCESS_TOKEN.
    If DEBUG_ACCESS_TOKEN is not configured, debug access is disabled in production.
    """
    if not ctx.DEBUG:
        # In production, validate token
        if settings.debug_access_token is None:
            raise HTTPException(status_code=404, detail="Not found")
        if token is None or token != settings.debug_access_token:
            raise HTTPException(status_code=404, detail="Not found")

    response = RedirectResponse(url="/debug", status_code=302)
    response.set_cookie(
        key=MAGIC_COOKIE_NAME,
        value="granted",
        httponly=True,
        secure=not ctx.DEBUG,  # Only secure in production
        samesite="lax",
        max_age=86400 * 30,  # 30 days
    )
    return response


@auth_router.get("/_lock-debug")
def lock_debug_access():
    """Revoke debug access by removing the magic cookie."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key=MAGIC_COOKIE_NAME)
    return response


# Protected router for debug endpoints requiring cookie auth
router = APIRouter(prefix="/debug", dependencies=[Depends(check_debug_access)])


@router.get("/", response_class=HTMLResponse)
def debug_index(request: Request):
    return render_template("debug/index.html.jinja", request)


@router.get("/version", response_class=HTMLResponse)
def debug_version(request: Request):
    return render_template("debug/version.html.jinja", request)


@router.get("/info", response_class=HTMLResponse)
def debug_info(request: Request):
    cookies = dict(request.cookies)
    return render_template("debug/info.html.jinja", request, {"cookies": cookies})


def _extract_ref_name(ref: str) -> str:
    """Extract type name from JSON schema $ref."""
    return ref.split("/")[-1]


def _parse_array_type(field_info: dict, field_name: str = "") -> str:
    """Parse array field type from JSON schema."""
    if "items" not in field_info:
        return "array[object]"

    items = field_info["items"]
    items_type = items.get("type", "")

    # Handle union types in arrays (anyOf, oneOf)
    if "anyOf" in items:
        union_types = _parse_union_types(items, "anyOf", field_name)
        return f"array[{union_types}]"
    elif "oneOf" in items:
        union_types = _parse_union_types(items, "oneOf", field_name)
        return f"array[{union_types}]"
    # Handle object references
    elif items_type == "object" and "$ref" in items:
        ref_name = _extract_ref_name(items["$ref"])
        return f"array[{ref_name}]"
    elif "$ref" in items:
        ref_name = _extract_ref_name(items["$ref"])
        return f"array[{ref_name}]"
    # Handle nested arrays
    elif items_type == "array":
        nested_array_type = _parse_array_type(items, field_name)
        return f"array[{nested_array_type}]"
    else:
        return f"array[{items_type or 'object'}]"


def _is_beanie_link_schema(option: dict) -> bool:
    """Check if this schema represents a Beanie Link."""
    if option.get("type") != "object":
        return False

    properties = option.get("properties", {})
    required = option.get("required", [])

    # Beanie Link has id and collection properties
    return (
        "id" in properties
        and "collection" in properties
        and "id" in required
        and "collection" in required
        and len(properties) == 2
    )


def _infer_link_target_from_field_name(field_name: str) -> str:
    """Infer the target model type from field name patterns."""
    # Core vibetuner models
    patterns = {
        "oauth_accounts": "OAuthAccountModel",
        "users": "UserModel",
        "user": "UserModel",
        "blobs": "BlobModel",
        "blob": "BlobModel",
    }

    # Direct lookup
    if field_name in patterns:
        return patterns[field_name]

    # Try singular/plural conversions
    if field_name.endswith("s"):
        singular = field_name[:-1]
        if singular in patterns:
            return patterns[singular]

    # Pattern-based inference (field_name -> FieldNameModel)
    if "_" in field_name:
        # Convert snake_case to PascalCase
        parts = field_name.split("_")
        model_name = "".join(word.capitalize() for word in parts) + "Model"
        return model_name
    else:
        # Simple case: field_name -> FieldNameModel
        return field_name.capitalize() + "Model"


def _process_union_option(option: dict) -> tuple[str | None, bool]:
    """Process a single union option, return (type_name, is_link)."""
    if "type" in option:
        if _is_beanie_link_schema(option):
            return None, True
        else:
            return option["type"], False
    elif "$ref" in option:
        ref_name = _extract_ref_name(option["$ref"])
        return ref_name, False
    elif "const" in option:
        return f"'{option['const']}'", False
    else:
        if option.get("type") == "object" and option.get("additionalProperties"):
            return None, False  # Skip generic objects from Links
        return "object", False


def _parse_union_types(field_info: dict, union_key: str, field_name: str = "") -> str:
    """Parse union types (anyOf, oneOf) from JSON schema."""
    types = []
    has_link = False

    for option in field_info[union_key]:
        type_name, is_link = _process_union_option(option)
        if is_link:
            has_link = True
        elif type_name:
            types.append(type_name)

    if not types:
        return union_key

    # Add Link indicator with inferred target type
    if has_link:
        if field_name:
            target_type = _infer_link_target_from_field_name(field_name)
            return f"Link[{target_type}]"
        else:
            return f"Link[{types[0] if types else 'object'}]"

    # If we have many types, show count to keep display clean
    if len(types) > 4:
        return f"{len(types)} types"

    return " | ".join(types)


def _handle_fallback_type(field_info: dict, field_name: str) -> str:
    """Handle fallback type inference when no explicit type is provided."""
    if "properties" in field_info:
        return "object"
    elif "items" in field_info:
        return "array"
    elif "format" in field_info:
        return field_info["format"]
    else:
        return field_name.split("_")[-1] if "_" in field_name else "any"


def _parse_field_type(field_info: dict, field_name: str) -> str:
    """Parse field type from JSON schema field info."""
    field_type = field_info.get("type", "")

    # Handle array types
    if field_type == "array":
        return _parse_array_type(field_info, field_name)

    # Handle object references
    if "$ref" in field_info:
        return _extract_ref_name(field_info["$ref"])

    # Handle union types
    if "anyOf" in field_info:
        return _parse_union_types(field_info, "anyOf", field_name)

    if "oneOf" in field_info:
        return _parse_union_types(field_info, "oneOf", field_name)

    # Handle inheritance
    if "allOf" in field_info:
        return "object"

    # Handle const values
    if "const" in field_info:
        return f"const({field_info['const']})"

    # Handle enum values
    if "enum" in field_info:
        return f"enum({len(field_info['enum'])} values)"

    # Fallback type inference
    if not field_type:
        return _handle_fallback_type(field_info, field_name)

    return field_type


def _get_extra_field_info(field_info: dict) -> dict:
    """Extract additional field metadata."""
    extra = {}

    # Add constraints if present
    if "minimum" in field_info:
        extra["min"] = field_info["minimum"]
    if "maximum" in field_info:
        extra["max"] = field_info["maximum"]
    if "minLength" in field_info:
        extra["min_length"] = field_info["minLength"]
    if "maxLength" in field_info:
        extra["max_length"] = field_info["maxLength"]
    if "pattern" in field_info:
        extra["pattern"] = field_info["pattern"]
    if "format" in field_info:
        extra["format"] = field_info["format"]
    if "default" in field_info:
        extra["default"] = field_info["default"]
    if "enum" in field_info:
        enum_values = field_info["enum"]
        if len(enum_values) <= 5:
            extra["enum"] = enum_values
        else:
            extra["enum_count"] = len(enum_values)

    return extra


def _extract_fields_from_schema(schema: dict) -> list[dict]:
    """Extract field information from JSON schema."""
    fields: list[dict] = []

    if "properties" not in schema:
        return fields

    for field_name, field_info in schema["properties"].items():
        field_type = _parse_field_type(field_info, field_name)
        field_description = field_info.get("description", "")
        required = field_name in schema.get("required", [])
        extra_info = _get_extra_field_info(field_info)

        fields.append(
            {
                "name": field_name,
                "type": field_type,
                "required": required,
                "description": field_description,
                "extra": extra_info,
            }
        )

    return fields


def _get_collection_info(model) -> dict:
    """Extract collection information from a Beanie model."""
    if hasattr(model, "Settings") and hasattr(model.Settings, "name"):
        collection_name = model.Settings.name
    else:
        collection_name = model.__name__.lower()

    schema = model.model_json_schema()
    fields = _extract_fields_from_schema(schema)

    return {
        "name": collection_name,
        "model_name": model.__name__,
        "fields": fields,
        "total_fields": len(fields),
    }


@router.get("/collections", response_class=HTMLResponse)
def debug_collections(request: Request):
    """Debug endpoint to display MongoDB collection schemas."""
    collections_info = [_get_collection_info(model) for model in get_all_models()]

    return render_template(
        "debug/collections.html.jinja", request, {"collections": collections_info}
    )


@router.get("/users", response_class=HTMLResponse)
async def debug_users(request: Request):
    """Debug endpoint to list and impersonate users."""

    users = await UserModel.find_all().to_list()
    current_user_id = (
        request.session.get("user", {}).get("id")
        if isinstance(request.session.get("user"), dict)
        else request.session.get("user")
    )

    return render_template(
        "debug/users.html.jinja",
        request,
        {"users": users, "current_user_id": current_user_id},
    )


# The following endpoints are restricted to DEBUG mode only (no production access).
# These are dangerous operations that could compromise security if allowed in production.


@router.post("/impersonate/{user_id}")
async def debug_impersonate_user(request: Request, user_id: str):
    """Impersonate a user by setting their ID in the session."""
    if not ctx.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    # Verify user exists
    user = await UserModel.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Set full user session data (using the proper session_dict method)
    request.session["user"] = user.session_dict

    return RedirectResponse(url="/", status_code=302)


@router.post("/stop-impersonation")
async def debug_stop_impersonation(request: Request):
    """Stop impersonating and clear user session."""
    if not ctx.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    request.session.pop("user", None)
    return RedirectResponse(url="/debug/users", status_code=302)


@router.get("/clear-session")
async def debug_clear_session(request: Request):
    """Clear all session data to fix corrupted sessions."""
    if not ctx.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    request.session.clear()
    return RedirectResponse(url="/debug/users?cleared=1", status_code=302)


# Runtime Configuration Routes


@router.get("/config", response_class=HTMLResponse)
async def debug_config(request: Request):
    """Debug endpoint to view runtime configuration."""
    from vibetuner.runtime_config import RuntimeConfig

    entries = await RuntimeConfig.get_all_config()
    return render_template(
        "debug/config.html.jinja",
        request,
        {
            "entries": entries,
            "mongodb_available": settings.mongodb_url is not None,
            "cache_stale": RuntimeConfig.is_cache_stale(),
        },
    )


@router.get("/config/{key:path}", response_class=HTMLResponse)
async def debug_config_detail(request: Request, key: str):
    """Debug endpoint to view/edit a single config entry."""
    from vibetuner.runtime_config import RuntimeConfig

    # Find the entry
    entries = await RuntimeConfig.get_all_config()
    entry = next((e for e in entries if e["key"] == key), None)

    if not entry:
        raise HTTPException(status_code=404, detail="Config entry not found")

    return render_template(
        "debug/config_detail.html.jinja",
        request,
        {
            "entry": entry,
            "mongodb_available": settings.mongodb_url is not None,
        },
    )


@router.post("/config/refresh")
async def debug_config_refresh(request: Request):
    """Force refresh of config cache from MongoDB."""
    from vibetuner.runtime_config import RuntimeConfig

    await RuntimeConfig.refresh_cache()
    return RedirectResponse(url="/debug/config", status_code=302)


@router.post("/config/{key:path}")
async def debug_config_update(request: Request, key: str):
    """Update a config value (DEBUG mode only, non-secrets)."""
    if not ctx.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    from vibetuner.runtime_config import RuntimeConfig

    # Find the entry to get its type and check if secret
    entries = await RuntimeConfig.get_all_config()
    entry = next((e for e in entries if e["key"] == key), None)

    if not entry:
        raise HTTPException(status_code=404, detail="Config entry not found")

    if entry["is_secret"]:
        raise HTTPException(status_code=403, detail="Cannot edit secret config")

    # Parse form data
    form = await request.form()
    raw_value = form.get("value", "")
    persist = form.get("persist") == "on"

    # Validate and convert value
    validated_value = RuntimeConfig._validate_value(raw_value, entry["value_type"])

    if persist and settings.mongodb_url is not None:
        # Persist to MongoDB
        await RuntimeConfig.set_value(
            key=key,
            value=validated_value,
            value_type=entry["value_type"],
            description=entry["description"],
            category=entry["category"],
            is_secret=entry["is_secret"],
        )
    else:
        # Set as runtime override only
        await RuntimeConfig.set_runtime_override(key, validated_value)

    return RedirectResponse(url="/debug/config", status_code=302)


@router.post("/config/{key:path}/clear-override")
async def debug_config_clear_override(request: Request, key: str):
    """Remove runtime override for a config entry (DEBUG mode only)."""
    if not ctx.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    from vibetuner.runtime_config import RuntimeConfig

    await RuntimeConfig.clear_runtime_override(key)
    return RedirectResponse(url=f"/debug/config/{key}", status_code=302)


# Claude Code Notification Routes


async def _broadcast_claude_event(event: dict[str, Any]) -> None:
    """Broadcast an event to all connected SSE subscribers."""
    for queue in _claude_subscribers:
        await queue.put(event)


@router.post("/claude/webhook")
async def debug_claude_webhook(request: Request):
    """Receive Claude Code hook events and broadcast to SSE subscribers.

    Called by `vibetuner notify` CLI command when Claude hooks fire.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    event = {
        "type": payload.get("event", "unknown"),
        "payload": payload,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    _claude_events.append(event)
    await _broadcast_claude_event(event)

    return {"status": "ok"}


async def _event_generator(queue: asyncio.Queue):
    """Generate SSE events from the queue."""
    shutdown_event = _get_shutdown_event()
    try:
        while not shutdown_event.is_set():
            try:
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield {
                    "event": event["type"],
                    "data": event,
                }
            except asyncio.TimeoutError:
                continue
    except asyncio.CancelledError:
        pass


@router.get("/claude/events")
async def debug_claude_events(request: Request):
    """SSE endpoint for Claude Code events.

    Browsers connect here to receive real-time notifications.
    """
    queue: asyncio.Queue = asyncio.Queue()
    _claude_subscribers.add(queue)

    async def event_stream():
        try:
            async for event in _event_generator(queue):
                yield event
        finally:
            _claude_subscribers.discard(queue)

    return EventSourceResponse(event_stream())


@router.get("/claude", response_class=HTMLResponse)
async def debug_claude(request: Request):
    """Debug page showing Claude Code events with live updates."""
    return render_template(
        "debug/claude.html.jinja",
        request,
        {"events": list(_claude_events)},
    )
