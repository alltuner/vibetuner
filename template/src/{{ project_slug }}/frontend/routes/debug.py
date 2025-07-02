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


@router.get("/collections", response_class=HTMLResponse)
def debug_collections(request: Request):
    # Extract schema information from Beanie models
    collections_info = []

    for model in models:
        if hasattr(model, "Settings") and hasattr(model.Settings, "name"):
            collection_name = model.Settings.name
        else:
            collection_name = model.__name__.lower()

        # Get model schema
        schema = model.model_json_schema()

        # Extract field information
        fields = []
        if "properties" in schema:
            for field_name, field_info in schema["properties"].items():
                field_type = field_info.get("type", "")
                field_description = field_info.get("description", "")
                required = field_name in schema.get("required", [])

                # Handle array types
                if field_type == "array" and "items" in field_info:
                    items_type = field_info["items"].get("type", "")
                    if items_type == "object" and "$ref" in field_info["items"]:
                        # Extract reference type name
                        ref_name = field_info["items"]["$ref"].split("/")[-1]
                        field_type = f"array[{ref_name}]"
                    elif "$ref" in field_info["items"]:
                        ref_name = field_info["items"]["$ref"].split("/")[-1]
                        field_type = f"array[{ref_name}]"
                    else:
                        field_type = f"array[{items_type or 'object'}]"

                # Handle object references
                elif "$ref" in field_info:
                    ref_name = field_info["$ref"].split("/")[-1]
                    field_type = ref_name

                # Handle union types (anyOf, oneOf)
                elif "anyOf" in field_info:
                    types = []
                    for option in field_info["anyOf"]:
                        if "type" in option:
                            types.append(option["type"])
                        elif "$ref" in option:
                            types.append(option["$ref"].split("/")[-1])
                    field_type = " | ".join(types) if types else "union"

                elif "oneOf" in field_info:
                    types = []
                    for option in field_info["oneOf"]:
                        if "type" in option:
                            types.append(option["type"])
                        elif "$ref" in option:
                            types.append(option["$ref"].split("/")[-1])
                    field_type = " | ".join(types) if types else "oneOf"

                # Handle allOf (inheritance)
                elif "allOf" in field_info:
                    field_type = "object"

                # Handle const values
                elif "const" in field_info:
                    field_type = f"const({field_info['const']})"

                # Handle enum values
                elif "enum" in field_info:
                    field_type = f"enum({len(field_info['enum'])} values)"

                # If still no type, try to infer from other properties
                if not field_type:
                    if "properties" in field_info:
                        field_type = "object"
                    elif "items" in field_info:
                        field_type = "array"
                    elif "format" in field_info:
                        field_type = field_info["format"]
                    else:
                        field_type = (
                            field_name.split("_")[-1] if "_" in field_name else "any"
                        )

                fields.append(
                    {
                        "name": field_name,
                        "type": field_type,
                        "required": required,
                        "description": field_description,
                    }
                )

        collections_info.append(
            {
                "name": collection_name,
                "model_name": model.__name__,
                "fields": fields,
                "total_fields": len(fields),
            }
        )

    return template_render(
        "debug/collections.html.jinja", request, {"collections": collections_info}
    )
