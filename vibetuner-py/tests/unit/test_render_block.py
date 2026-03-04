# ruff: noqa: S101
"""Tests for render_template_block() and render_template_blocks()."""

from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse


def _make_mock_template(blocks: dict[str, str]):
    """Create a mock template with named blocks."""
    mock = MagicMock()
    block_funcs = {}
    for name, content in blocks.items():

        def make_func(c):
            def block_func(context):
                return iter([c])

            return block_func

        block_funcs[name] = make_func(content)

    mock.blocks = block_funcs
    mock.new_context.side_effect = lambda ctx: ctx
    return mock


class TestRenderTemplateBlock:
    """Test single block rendering."""

    @patch("vibetuner.rendering._build_merged_ctx", return_value={"key": "val"})
    @patch("vibetuner.rendering.templates")
    def test_renders_single_block(self, mock_templates, mock_build_ctx):
        """Renders a single named block."""
        from vibetuner.rendering import render_template_block

        mock_templates.get_template.return_value = _make_mock_template(
            {"items_list": "<div>Items</div>", "sidebar": "<aside>Side</aside>"}
        )
        request = MagicMock(spec=Request)

        result = render_template_block(
            "items/list.html.jinja", "items_list", request, {"items": []}
        )

        assert isinstance(result, HTMLResponse)
        assert result.body == b"<div>Items</div>"

    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    @patch("vibetuner.rendering.templates")
    def test_missing_block_raises_value_error(self, mock_templates, mock_build_ctx):
        """Missing block raises ValueError with available blocks."""
        from vibetuner.rendering import render_template_block

        mock_templates.get_template.return_value = _make_mock_template(
            {"body": "content"}
        )
        request = MagicMock(spec=Request)

        with pytest.raises(ValueError, match="Block 'missing' not found"):
            render_template_block("t.html.jinja", "missing", request)

    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    @patch("vibetuner.rendering.templates")
    def test_error_message_lists_available_blocks(self, mock_templates, mock_build_ctx):
        """Error message includes available block names."""
        from vibetuner.rendering import render_template_block

        mock_templates.get_template.return_value = _make_mock_template(
            {"header": "h", "body": "b", "footer": "f"}
        )
        request = MagicMock(spec=Request)

        with pytest.raises(ValueError, match="Available blocks:"):
            render_template_block("t.html.jinja", "sidebar", request)


class TestRenderTemplateBlocks:
    """Test multi-block rendering."""

    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    @patch("vibetuner.rendering.templates")
    def test_renders_multiple_blocks_concatenated(self, mock_templates, mock_build_ctx):
        """Renders multiple blocks concatenated."""
        from vibetuner.rendering import render_template_blocks

        mock_templates.get_template.return_value = _make_mock_template(
            {
                "items_list": '<div id="items">Items</div>',
                "badge": '<span id="count" hx-swap-oob="true">5</span>',
            }
        )
        request = MagicMock(spec=Request)

        result = render_template_blocks(
            "items/list.html.jinja", ["items_list", "badge"], request
        )

        assert isinstance(result, HTMLResponse)
        assert (
            result.body == b'<div id="items">Items</div>'
            b'<span id="count" hx-swap-oob="true">5</span>'
        )

    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    @patch("vibetuner.rendering.templates")
    def test_missing_block_in_list_raises(self, mock_templates, mock_build_ctx):
        """Missing block in list raises ValueError."""
        from vibetuner.rendering import render_template_blocks

        mock_templates.get_template.return_value = _make_mock_template(
            {"items_list": "items"}
        )
        request = MagicMock(spec=Request)

        with pytest.raises(ValueError, match="Block 'badge' not found"):
            render_template_blocks("t.html.jinja", ["items_list", "badge"], request)

    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    @patch("vibetuner.rendering.templates")
    def test_single_block_in_list(self, mock_templates, mock_build_ctx):
        """Single block in list works."""
        from vibetuner.rendering import render_template_blocks

        mock_templates.get_template.return_value = _make_mock_template(
            {"body": "<main>Content</main>"}
        )
        request = MagicMock(spec=Request)

        result = render_template_blocks("t.html.jinja", ["body"], request)
        assert result.body == b"<main>Content</main>"
