from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from ...models import MODELS
from ..context import ctx
from ..deps import MAGIC_COOKIE_NAME
from ..templates import render_template


def check_debug_access(request: Request, prod: str | None = None):
    """Check if debug routes should be accessible."""
    # Always allow in development mode
    if ctx.DEBUG:
        return True

    # In production, require prod=1 parameter
    if prod == "1":
        return True

    # Deny access
    raise HTTPException(status_code=404, detail="Not found")


router = APIRouter(prefix="/debug", dependencies=[Depends(check_debug_access)])


@router.get("/", response_class=HTMLResponse)
def debug_index(request: Request):
    return render_template("debug/index.html.jinja", request)


@router.get("/health")
def health():
    return {"ping": "ok"}


@router.get("/magic")
def set_magic_cookie(response: Response):
    """Set the magic access cookie."""
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key=MAGIC_COOKIE_NAME,
        value="granted",
        httponly=True,
        secure=not ctx.DEBUG,  # Only secure in production
        samesite="lax",
        max_age=86400 * 30,  # 30 days
    )
    return response


@router.get("/no-magic")
def remove_magic_cookie(response: Response):
    """Remove the magic access cookie."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key=MAGIC_COOKIE_NAME)
    return response


@router.get("/version", response_class=HTMLResponse)
def debug_version(request: Request):
    return render_template("debug/version.html.jinja", request)


@router.get("/info", response_class=HTMLResponse)
def debug_info(request: Request):
    # Get cookies from request
    cookies = dict(request.cookies)

    # Get language from request state
    language = getattr(request.state, "language", "Not set")

    return render_template(
        "debug/info.html.jinja", request, {"cookies": cookies, "language": language}
    )


def _extract_ref_name(ref: str) -> str:
    """Extract type name from JSON schema $ref."""
    return ref.split("/")[-1]


def _parse_array_type(field_info: dict) -> str:
    """Parse array field type from JSON schema."""
    if "items" not in field_info:
        return "array[object]"

    items = field_info["items"]
    items_type = items.get("type", "")

    if items_type == "object" and "$ref" in items:
        ref_name = _extract_ref_name(items["$ref"])
        return f"array[{ref_name}]"
    elif "$ref" in items:
        ref_name = _extract_ref_name(items["$ref"])
        return f"array[{ref_name}]"
    else:
        return f"array[{items_type or 'object'}]"


def _parse_union_types(field_info: dict, union_key: str) -> str:
    """Parse union types (anyOf, oneOf) from JSON schema."""
    types = []
    for option in field_info[union_key]:
        if "type" in option:
            types.append(option["type"])
        elif "$ref" in option:
            types.append(_extract_ref_name(option["$ref"]))
    return " | ".join(types) if types else union_key


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
        return _parse_array_type(field_info)

    # Handle object references
    if "$ref" in field_info:
        return _extract_ref_name(field_info["$ref"])

    # Handle union types
    if "anyOf" in field_info:
        return _parse_union_types(field_info, "anyOf")

    if "oneOf" in field_info:
        return _parse_union_types(field_info, "oneOf")

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


def _extract_fields_from_schema(schema: dict) -> list[dict]:
    """Extract field information from JSON schema."""
    fields: list[dict] = []

    if "properties" not in schema:
        return fields

    for field_name, field_info in schema["properties"].items():
        field_type = _parse_field_type(field_info, field_name)
        field_description = field_info.get("description", "")
        required = field_name in schema.get("required", [])

        fields.append(
            {
                "name": field_name,
                "type": field_type,
                "required": required,
                "description": field_description,
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
    collections_info = [_get_collection_info(model) for model in MODELS]

    return render_template(
        "debug/collections.html.jinja", request, {"collections": collections_info}
    )
