# ABOUTME: Generic CRUD route factory for Beanie Document and SQLModel classes.
# ABOUTME: Generates list/create/read/update/delete routes with pagination, filtering, and sorting.
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from beanie import Document, PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from vibetuner.logging import logger


class Operation(StrEnum):
    """CRUD operations that can be enabled/disabled."""

    LIST = "list"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


ALL_OPERATIONS: set[Operation] = set(Operation)

PreHook = Callable[..., Any]
PostHook = Callable[..., Any]


# ────────────────────────────────────────────────────────────────
#  Query helpers
# ────────────────────────────────────────────────────────────────


def _apply_filters(query, request: Request, filterable: list[str]):
    """Apply equality filters from query params."""
    for field_name in filterable:
        value = request.query_params.get(field_name)
        if value is not None:
            query = query.find({field_name: value})
    return query


def _apply_search(query, request: Request, searchable: list[str]):
    """Apply text search across searchable fields."""
    q = request.query_params.get("q")
    if q and searchable:
        search_filter = {
            "$or": [{f: {"$regex": q, "$options": "i"}} for f in searchable]
        }
        query = query.find(search_filter)
    return query


def _apply_sort(query, sort: str | None, sortable: list[str]):
    """Apply sorting to a query."""
    if not sort or not sortable:
        return query
    sort_parts = []
    for part in sort.split(","):
        part = part.strip()
        if part.startswith("-"):
            field, direction = part[1:], "-"
        else:
            field, direction = part.lstrip("+"), "+"
        if field in sortable:
            sort_parts.append(f"{direction}{field}")
    if sort_parts:
        query = query.sort(sort_parts)
    return query


def _serialize_items(
    items: list,
    fields: str | None,
    response_schema: type[BaseModel] | None,
) -> list:
    """Serialize items with optional field selection and response schema."""
    if fields:
        selected = {f.strip() for f in fields.split(",")}
        return [_select_fields(item, selected, response_schema) for item in items]
    if response_schema:
        return [response_schema.model_validate(item.model_dump()) for item in items]
    return items


def _serialize_one(doc: Document, response_schema: type[BaseModel] | None):
    """Serialize a single document with optional response schema."""
    if response_schema:
        return response_schema.model_validate(doc.model_dump())
    return doc


# ────────────────────────────────────────────────────────────────
#  Route registration helpers
# ────────────────────────────────────────────────────────────────


def _register_list_route(
    router: APIRouter,
    model: type[Document],
    collection_name: str,
    page_size: int,
    max_page_size: int,
    filterable: list[str],
    searchable: list[str],
    sortable: list[str],
    response_schema: type[BaseModel] | None,
) -> None:
    @router.get("", name=f"{collection_name}_list")
    async def list_items(
        request: Request,
        offset: int = Query(0, ge=0),
        limit: int = Query(page_size, ge=1, le=max_page_size),
        sort: str | None = Query(None),
        fields: str | None = Query(
            None, description="Comma-separated field names to include"
        ),
    ):
        query = model.find()
        query = _apply_filters(query, request, filterable)
        query = _apply_search(query, request, searchable)
        query = _apply_sort(query, sort, sortable)

        total = await query.count()
        items = await query.skip(offset).limit(limit).to_list()

        return {
            "items": _serialize_items(items, fields, response_schema),
            "total": total,
            "offset": offset,
            "limit": limit,
        }


def _register_create_route(
    router: APIRouter,
    model: type[Document],
    collection_name: str,
    schema: type[BaseModel],
    response_schema: type[BaseModel] | None,
    pre_create: PreHook | None,
    post_create: PostHook | None,
) -> None:
    @router.post("", name=f"{collection_name}_create", status_code=201)
    async def create_item(request: Request, data: schema):  # type: ignore[valid-type]
        if pre_create:
            data = await pre_create(data, request) or data

        doc = model(**data.model_dump())
        await doc.insert()

        if post_create:
            await post_create(doc, request)

        return _serialize_one(doc, response_schema)


def _register_read_route(
    router: APIRouter,
    model: type[Document],
    collection_name: str,
    response_schema: type[BaseModel] | None,
) -> None:
    @router.get("/{item_id}", name=f"{collection_name}_read")
    async def read_item(item_id: PydanticObjectId, fields: str | None = Query(None)):
        doc = await model.get(item_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Not found")

        if fields:
            selected = {f.strip() for f in fields.split(",")}
            return _select_fields(doc, selected, response_schema)
        return _serialize_one(doc, response_schema)


def _register_update_route(
    router: APIRouter,
    model: type[Document],
    collection_name: str,
    schema: type[BaseModel],
    response_schema: type[BaseModel] | None,
    pre_update: PreHook | None,
    post_update: PostHook | None,
) -> None:
    @router.patch("/{item_id}", name=f"{collection_name}_update")
    async def update_item(
        request: Request,
        item_id: PydanticObjectId,
        data: schema,  # type: ignore[valid-type]
    ):
        doc = await model.get(item_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Not found")

        if pre_update:
            data = await pre_update(doc, data, request) or data

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await doc.set(update_data)

        if post_update:
            await post_update(doc, request)

        return _serialize_one(doc, response_schema)


def _register_delete_route(
    router: APIRouter,
    model: type[Document],
    collection_name: str,
    pre_delete: PreHook | None,
    post_delete: PostHook | None,
) -> None:
    @router.delete("/{item_id}", name=f"{collection_name}_delete", status_code=204)
    async def delete_item(request: Request, item_id: PydanticObjectId):
        doc = await model.get(item_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Not found")

        if pre_delete:
            await pre_delete(doc, request)

        await doc.delete()

        if post_delete:
            await post_delete(doc, request)

        return None


# ────────────────────────────────────────────────────────────────
#  Public API
# ────────────────────────────────────────────────────────────────


def create_crud_routes(
    model: type[Document],
    *,
    prefix: str | None = None,
    tags: list[str] | None = None,
    operations: set[Operation] | None = None,
    page_size: int = 25,
    max_page_size: int = 100,
    sortable_fields: list[str] | None = None,
    filterable_fields: list[str] | None = None,
    searchable_fields: list[str] | None = None,
    dependencies: list[Any] | None = None,
    pre_create: PreHook | None = None,
    post_create: PostHook | None = None,
    pre_update: PreHook | None = None,
    post_update: PostHook | None = None,
    pre_delete: PreHook | None = None,
    post_delete: PostHook | None = None,
    create_schema: type[BaseModel] | None = None,
    update_schema: type[BaseModel] | None = None,
    response_schema: type[BaseModel] | None = None,
) -> APIRouter:
    """Create a full set of CRUD routes for a Beanie Document model.

    Args:
        model: Beanie Document class to generate routes for.
        prefix: URL prefix (defaults to "/{collection_name}").
        tags: OpenAPI tags for the routes.
        operations: Set of operations to generate. Defaults to all.
        page_size: Default items per page.
        max_page_size: Maximum allowed items per page.
        sortable_fields: Fields that can be used for sorting.
        filterable_fields: Fields that support equality filtering via query params.
        searchable_fields: Fields that support text search.
        dependencies: FastAPI dependencies applied to all routes.
        pre_create: Async callable(data, request) called before creating a document.
        post_create: Async callable(doc, request) called after creation.
        pre_update: Async callable(doc, data, request) called before updating.
        post_update: Async callable(doc, request) called after updating.
        pre_delete: Async callable(doc, request) called before deletion.
        post_delete: Async callable(doc, request) called after deletion.
        create_schema: Pydantic model for create payloads (defaults to model fields).
        update_schema: Pydantic model for update payloads (defaults to create_schema).
        response_schema: Pydantic model for response serialization.

    Returns:
        APIRouter with CRUD endpoints.

    Example:
        from vibetuner.crud import create_crud_routes
        from myapp.models import Post

        post_routes = create_crud_routes(
            Post,
            prefix="/posts",
            tags=["posts"],
            sortable_fields=["created_at", "title"],
            filterable_fields=["status", "author_id"],
        )
        app.include_router(post_routes)
    """
    collection_name = _get_collection_name(model)
    prefix = prefix or f"/{collection_name}"
    tags = tags or [collection_name]
    ops = operations or ALL_OPERATIONS
    sortable = sortable_fields or []
    filterable = filterable_fields or []
    searchable = searchable_fields or []
    deps = dependencies or []

    router = APIRouter(
        prefix=prefix,
        tags=tags,
        dependencies=[Depends(d) for d in deps] if deps else [],
    )

    if Operation.LIST in ops:
        _register_list_route(
            router,
            model,
            collection_name,
            page_size,
            max_page_size,
            filterable,
            searchable,
            sortable,
            response_schema,
        )

    if Operation.CREATE in ops:
        _cs = create_schema or _build_create_schema(model)
        _register_create_route(
            router,
            model,
            collection_name,
            _cs,
            response_schema,
            pre_create,
            post_create,
        )

    if Operation.READ in ops:
        _register_read_route(router, model, collection_name, response_schema)

    if Operation.UPDATE in ops:
        _us = update_schema or _build_update_schema(
            create_schema or _build_create_schema(model)
        )
        _register_update_route(
            router,
            model,
            collection_name,
            _us,
            response_schema,
            pre_update,
            post_update,
        )

    if Operation.DELETE in ops:
        _register_delete_route(router, model, collection_name, pre_delete, post_delete)

    logger.debug(
        "Created CRUD routes for {} at {} (operations: {})",
        model.__name__,
        prefix,
        ", ".join(sorted(ops)),
    )

    return router


# ────────────────────────────────────────────────────────────────
#  Helpers
# ────────────────────────────────────────────────────────────────


def _get_collection_name(model: type[Document]) -> str:
    """Get the collection name from a Beanie Document."""
    if hasattr(model, "Settings") and hasattr(model.Settings, "name"):
        return model.Settings.name
    return model.__name__.lower().rstrip("model") or model.__name__.lower()


def _build_create_schema(model: type[Document]) -> type[BaseModel]:
    """Build a Pydantic create schema from a Beanie Document, excluding id and internal fields."""
    excluded = {"id", "revision_id", "db_insert_dt", "db_update_dt"}
    fields: dict[str, Any] = {}
    for name, field_info in model.model_fields.items():
        if name in excluded:
            continue
        fields[name] = (field_info.annotation, field_info)

    return type(
        f"{model.__name__}Create",
        (BaseModel,),
        {
            "__annotations__": {n: t for n, (t, _) in fields.items()},
            **{n: f for n, (_, f) in fields.items()},
        },
    )


def _build_update_schema(create_schema: type[BaseModel]) -> type[BaseModel]:
    """Build a partial update schema from a create schema with all fields Optional."""
    fields: dict[str, Any] = {}
    for name, field_info in create_schema.model_fields.items():
        fields[name] = (field_info.annotation | None, None)

    return type(
        f"{create_schema.__name__.removesuffix('Create')}Update",
        (BaseModel,),
        {
            "__annotations__": {n: t for n, (t, _) in fields.items()},
            **{n: default for n, (_, default) in fields.items()},
        },
    )


def _select_fields(
    doc: Document,
    selected: set[str],
    response_schema: type[BaseModel] | None = None,
) -> dict[str, Any]:
    """Return only the selected fields from a document."""
    data = doc.model_dump()
    filtered = {k: v for k, v in data.items() if k in selected or k == "id"}
    if "id" in filtered:
        filtered["id"] = str(doc.id)
    if response_schema:
        return response_schema.model_validate(filtered).model_dump(
            include=selected | {"id"}
        )
    return filtered
