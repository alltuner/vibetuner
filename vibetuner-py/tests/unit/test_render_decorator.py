# ruff: noqa: S101
"""Tests for the @render(template) decorator."""

from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from vibetuner.rendering import render


class TestRenderDecorator:
    """Test the @render() decorator."""

    @patch("vibetuner.rendering.render_template")
    @pytest.mark.asyncio
    async def test_async_route_returns_dict(self, mock_render_template):
        """Async route returning dict calls render_template."""
        mock_render_template.return_value = HTMLResponse("<html>ok</html>")
        request = MagicMock(spec=Request)

        @render("items/list.html.jinja")
        async def index(request: Request) -> dict:
            return {"items": [1, 2, 3]}

        result = await index(request=request)

        mock_render_template.assert_called_once_with(
            "items/list.html.jinja", request, {"items": [1, 2, 3]}
        )
        assert isinstance(result, HTMLResponse)

    @patch("vibetuner.rendering.render_template")
    @pytest.mark.asyncio
    async def test_sync_route_returns_dict(self, mock_render_template):
        """Sync route returning dict calls render_template."""
        mock_render_template.return_value = HTMLResponse("<html>ok</html>")
        request = MagicMock(spec=Request)

        @render("items/list.html.jinja")
        def index(request: Request) -> dict:
            return {"items": [1, 2, 3]}

        await index(request=request)

        mock_render_template.assert_called_once_with(
            "items/list.html.jinja", request, {"items": [1, 2, 3]}
        )

    @pytest.mark.asyncio
    async def test_passthrough_html_response(self):
        """HTMLResponse is passed through unchanged."""
        request = MagicMock(spec=Request)
        expected = HTMLResponse("<html>custom</html>")

        @render("items/list.html.jinja")
        async def index(request: Request):
            return expected

        result = await index(request=request)
        assert result is expected

    @pytest.mark.asyncio
    async def test_passthrough_redirect_response(self):
        """RedirectResponse is passed through unchanged."""
        request = MagicMock(spec=Request)
        expected = RedirectResponse("/login")

        @render("items/list.html.jinja")
        async def index(request: Request):
            return expected

        result = await index(request=request)
        assert result is expected

    @pytest.mark.asyncio
    async def test_request_from_positional_arg(self):
        """Request is extracted from positional args."""
        request = MagicMock(spec=Request)
        expected = HTMLResponse("<html>ok</html>")

        @render("items/list.html.jinja")
        async def index(request: Request):
            return expected

        result = await index(request)
        assert result is expected

    @pytest.mark.asyncio
    async def test_missing_request_raises_type_error(self):
        """Missing request parameter raises TypeError."""

        @render("items/list.html.jinja")
        async def index():
            return {}

        with pytest.raises(TypeError, match="must accept a 'request' parameter"):
            await index()

    @pytest.mark.asyncio
    async def test_non_dict_non_response_raises_type_error(self):
        """Returning non-dict, non-Response raises TypeError."""
        request = MagicMock(spec=Request)

        @render("items/list.html.jinja")
        async def index(request: Request):
            return "not a dict"

        with pytest.raises(TypeError, match="must return a dict or Response"):
            await index(request=request)

    @patch("vibetuner.rendering.render_template")
    @pytest.mark.asyncio
    async def test_empty_dict_context(self, mock_render_template):
        """Empty dict is a valid context."""
        mock_render_template.return_value = HTMLResponse("<html>ok</html>")
        request = MagicMock(spec=Request)

        @render("index.html.jinja")
        async def index(request: Request) -> dict:
            return {}

        await index(request=request)
        mock_render_template.assert_called_once_with("index.html.jinja", request, {})

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        """Wrapper preserves the original function name."""

        @render("items/list.html.jinja")
        async def my_custom_route(request: Request) -> dict:
            return {}

        assert my_custom_route.__name__ == "my_custom_route"
