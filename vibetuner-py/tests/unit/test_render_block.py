# ABOUTME: Tests render_template_block() and render_template_blocks() against real Jinja templates,
# ABOUTME: including that blocks see the template's top-level macro imports.
# ruff: noqa: S101
from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import pytest
from jinja2 import DictLoader, Environment
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates


TEMPLATES: dict[str, str] = {
    "ui.html.jinja": "{% macro badge(label) %}<b>{{ label }}</b>{% endmacro %}",
    "base.html.jinja": "<html>{% block content %}{% endblock %}</html>",
    "items/list.html.jinja": (
        '{% extends "base.html.jinja" %}'
        "{% block content %}"
        '{% block items_list %}<div id="items">Items</div>{% endblock %}'
        '{% block badge %}<span id="count" hx-swap-oob="true">{{ count }}</span>'
        "{% endblock %}"
        "{% endblock %}"
    ),
    "page.html.jinja": (
        '{% extends "base.html.jinja" %}'
        '{% from "ui.html.jinja" import badge %}'
        '{% import "ui.html.jinja" as ui %}'
        "{% block content %}<main>{% block feed %}"
        "{{ badge(title) }}{{ ui.badge(title) }}"
        "{% endblock %}</main>{% endblock %}"
        "{% block counter %}{{ badge(count) }}{% endblock %}"
    ),
    "standalone.html.jinja": (
        "<p>intro</p>"
        "{% block feed %}{{ badge(title) }}{% endblock %}"
        '{% from "ui.html.jinja" import badge %}'
    ),
}


def _build_ctx(request: Request, ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"request": request, **(ctx or {})}


@pytest.fixture(autouse=True)
def real_templates() -> Iterator[Jinja2Templates]:
    env = Environment(loader=DictLoader(TEMPLATES), autoescape=True)
    templates = Jinja2Templates(env=env)
    with (
        patch("vibetuner.rendering.templates", templates),
        patch("vibetuner.rendering._build_merged_ctx", side_effect=_build_ctx),
    ):
        yield templates


@pytest.fixture
def request_obj() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": []})


class TestRenderTemplateBlock:
    """Test single block rendering."""

    def test_renders_single_block(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_block

        result = render_template_block(
            "items/list.html.jinja", "items_list", request_obj, {"count": 5}
        )

        assert isinstance(result, HTMLResponse)
        assert result.body == b'<div id="items">Items</div>'

    def test_missing_block_raises_value_error(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_block

        with pytest.raises(ValueError, match="Block 'missing' not found"):
            render_template_block("items/list.html.jinja", "missing", request_obj)

    def test_error_message_lists_available_blocks(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_block

        with pytest.raises(
            ValueError,
            match=r"Available blocks: \['content', 'items_list', 'badge'\]",
        ):
            render_template_block("items/list.html.jinja", "sidebar", request_obj)

    def test_block_sees_top_level_imports(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_block

        result = render_template_block(
            "page.html.jinja", "feed", request_obj, {"title": "Hi"}
        )

        assert result.body == b"<b>Hi</b><b>Hi</b>"

    def test_nested_block_sees_top_level_imports(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_block

        result = render_template_block(
            "page.html.jinja", "content", request_obj, {"title": "Hi"}
        )

        assert result.body == b"<main><b>Hi</b><b>Hi</b></main>"

    def test_import_after_block_in_template_without_parent(
        self, request_obj: Request
    ) -> None:
        from vibetuner.rendering import render_template_block

        result = render_template_block(
            "standalone.html.jinja", "feed", request_obj, {"title": "Hi"}
        )

        assert result.body == b"<b>Hi</b>"


class TestRenderTemplateBlocks:
    """Test multi-block rendering."""

    def test_renders_multiple_blocks_concatenated(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_blocks

        result = render_template_blocks(
            "items/list.html.jinja", ["items_list", "badge"], request_obj, {"count": 5}
        )

        assert isinstance(result, HTMLResponse)
        assert (
            result.body == b'<div id="items">Items</div>'
            b'<span id="count" hx-swap-oob="true">5</span>'
        )

    def test_missing_block_in_list_raises(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_blocks

        with pytest.raises(ValueError, match="Block 'sidebar' not found"):
            render_template_blocks(
                "items/list.html.jinja", ["items_list", "sidebar"], request_obj
            )

    def test_single_block_in_list(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_blocks

        result = render_template_blocks(
            "items/list.html.jinja", ["items_list"], request_obj
        )

        assert result.body == b'<div id="items">Items</div>'

    def test_blocks_see_top_level_imports(self, request_obj: Request) -> None:
        from vibetuner.rendering import render_template_blocks

        result = render_template_blocks(
            "page.html.jinja",
            ["feed", "counter"],
            request_obj,
            {"title": "Hi", "count": 3},
        )

        assert result.body == b"<b>Hi</b><b>Hi</b><b>3</b>"
