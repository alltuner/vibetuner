from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ...mongo import models
from ..templates import template_render


router = APIRouter(prefix="/debug")


@router.get("/", response_class=HTMLResponse)
def debug_index(request: Request):
    return template_render("debug/index.html.jinja", request)


@router.get("/health")
def health():
    return {"ping": "ok"}


@router.get("/version", response_class=HTMLResponse)
def debug_version(request: Request):
    return template_render("debug/version.html.jinja", request)


@router.get("/info", response_class=HTMLResponse)
def debug_info(request: Request):
    # Get cookies from request
    cookies = dict(request.cookies)

    # Get language from request state
    language = getattr(request.state, "language", "Not set")

    return template_render(
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
        if "properties" in field_info:
            return "object"
        elif "items" in field_info:
            return "array"
        elif "format" in field_info:
            return field_info["format"]
        else:
            return field_name.split("_")[-1] if "_" in field_name else "any"

    return field_type


def _extract_fields_from_schema(schema: dict) -> list[dict]:
    """Extract field information from JSON schema."""
    fields = []

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
    collections_info = [_get_collection_info(model) for model in models]

    return template_render(
        "debug/collections.html.jinja", request, {"collections": collections_info}
    )
