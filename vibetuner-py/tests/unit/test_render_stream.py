# ruff: noqa: S101
"""Tests for render_template_stream()."""

from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import StreamingResponse


class TestRenderTemplateStream:
    """Test streaming template rendering."""

    @patch("vibetuner.rendering._ensure_custom_filters")
    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._collect_provider_context", return_value={})
    @patch("vibetuner.rendering.data_ctx")
    def test_returns_streaming_response(
        self,
        mock_data_ctx,
        mock_collect,
        mock_templates,
        mock_filters,
    ):
        """render_template_stream returns a StreamingResponse."""
        from vibetuner.rendering import render_template_stream

        mock_data_ctx.model_dump.return_value = {}
        mock_data_ctx.default_language = "en"

        mock_template = MagicMock()
        mock_template.generate.return_value = iter(["<html>", "ok", "</html>"])
        mock_templates.get_template.return_value = mock_template

        request = MagicMock(spec=Request)
        request.state.language = "en"

        result = render_template_stream("test.html.jinja", request, {"key": "val"})

        assert isinstance(result, StreamingResponse)
        assert result.media_type == "text/html"
        mock_templates.get_template.assert_called_once_with("test.html.jinja")

    @patch("vibetuner.rendering._ensure_custom_filters")
    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._collect_provider_context", return_value={})
    @patch("vibetuner.rendering.data_ctx")
    @pytest.mark.asyncio
    async def test_streams_chunks(
        self,
        mock_data_ctx,
        mock_collect,
        mock_templates,
        mock_filters,
    ):
        """Streaming response yields template chunks."""
        from vibetuner.rendering import render_template_stream

        mock_data_ctx.model_dump.return_value = {}
        mock_data_ctx.default_language = "en"

        chunks = ["<html>", "<body>", "content", "</body>", "</html>"]
        mock_template = MagicMock()
        mock_template.generate.return_value = iter(chunks)
        mock_templates.get_template.return_value = mock_template

        request = MagicMock(spec=Request)
        request.state.language = "en"

        result = render_template_stream("test.html.jinja", request)

        # Read all chunks from the streaming response body
        collected = []
        async for chunk in result.body_iterator:
            collected.append(chunk)

        assert collected == chunks

    @patch("vibetuner.rendering._ensure_custom_filters")
    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._collect_provider_context", return_value={})
    @patch("vibetuner.rendering.data_ctx")
    @pytest.mark.asyncio
    async def test_merges_context(
        self,
        mock_data_ctx,
        mock_collect,
        mock_templates,
        mock_filters,
    ):
        """Context is merged the same as render_template."""
        from vibetuner.rendering import render_template_stream

        mock_data_ctx.model_dump.return_value = {"project_name": "test"}
        mock_data_ctx.default_language = "en"

        mock_template = MagicMock()
        mock_template.generate.return_value = iter(["ok"])
        mock_templates.get_template.return_value = mock_template

        request = MagicMock(spec=Request)
        request.state.language = "ca"

        result = render_template_stream("t.html.jinja", request, {"items": [1]})

        # Consume the stream to trigger generate()
        async for _ in result.body_iterator:
            pass

        call_kwargs = mock_template.generate.call_args.kwargs
        assert call_kwargs["project_name"] == "test"
        assert call_kwargs["language"] == "ca"
        assert call_kwargs["items"] == [1]
        assert call_kwargs["request"] is request
