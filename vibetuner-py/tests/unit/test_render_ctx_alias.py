# ABOUTME: Verifies that render_template* accepts `context=` as an alias for `ctx=`,
# ABOUTME: rejects passing both at once, and rejects unknown kwargs (issue #1838).
# ruff: noqa: S101
"""Regression tests for issue #1838.

The original signature was ``render_template(template, request, ctx=None, **kwargs)``.
Because of the catch-all ``**kwargs``, callers who naturally typed ``context={...}``
had their argument silently swallowed (forwarded to ``TemplateResponse``, where the
positional ``merged_ctx`` already filled the ``context`` slot), and the template
rendered with no user context. This caused misleading ``UndefinedError`` failures.

The fix:

1. Make ``context=`` an explicit alias for ``ctx=`` (raising if both are given).
2. Drop the catch-all ``**kwargs`` — unknown keyword arguments now raise
   ``TypeError`` immediately at the call site.
"""

from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request


@pytest.fixture
def mock_request() -> MagicMock:
    return MagicMock(spec=Request)


class TestContextAliasOnRenderTemplate:
    """`context=` is accepted as an alias for `ctx=` on render_template."""

    @patch("vibetuner.rendering.templates")
    @patch(
        "vibetuner.rendering._build_merged_ctx",
        side_effect=lambda req, ctx: dict(ctx or {}),
    )
    def test_context_kwarg_reaches_template(
        self, mock_build, mock_templates, mock_request
    ):
        """`context=` is forwarded into the merged ctx (used to be silently dropped)."""
        from vibetuner.rendering import render_template

        render_template("home.html.jinja", mock_request, context={"hero": "h"})

        mock_build.assert_called_once_with(mock_request, {"hero": "h"})
        # And it actually reaches TemplateResponse as the merged context.
        args, _ = mock_templates.TemplateResponse.call_args
        assert args[0] == "home.html.jinja"
        assert args[1] == {"hero": "h"}

    @patch("vibetuner.rendering.templates")
    @patch(
        "vibetuner.rendering._build_merged_ctx",
        side_effect=lambda req, ctx: dict(ctx or {}),
    )
    def test_ctx_positional_still_works(self, mock_build, mock_templates, mock_request):
        from vibetuner.rendering import render_template

        render_template("home.html.jinja", mock_request, {"hero": "h"})

        mock_build.assert_called_once_with(mock_request, {"hero": "h"})

    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    def test_passing_both_ctx_and_context_raises(
        self, mock_build, mock_templates, mock_request
    ):
        from vibetuner.rendering import render_template

        with pytest.raises(TypeError, match="both 'ctx' and 'context'"):
            render_template(
                "home.html.jinja",
                mock_request,
                {"a": 1},
                context={"b": 2},
            )

    def test_unknown_kwarg_raises_type_error(self, mock_request):
        """Misspelled kwargs (e.g. `contxt=`) raise TypeError instead of being swallowed."""
        from vibetuner.rendering import render_template

        with pytest.raises(TypeError, match="unexpected keyword argument"):
            render_template("home.html.jinja", mock_request, contxt={"hero": "h"})


class TestContextAliasOnRenderTemplateString:
    @patch("vibetuner.rendering.templates")
    @patch(
        "vibetuner.rendering._build_merged_ctx",
        side_effect=lambda req, ctx: dict(ctx or {}),
    )
    def test_context_kwarg_reaches_template(
        self, mock_build, mock_templates, mock_request
    ):
        from vibetuner.rendering import render_template_string

        mock_templates.get_template.return_value = MagicMock(
            render=MagicMock(return_value="<p>ok</p>")
        )

        result = render_template_string(
            "partials/x.html.jinja", mock_request, context={"hero": "h"}
        )

        assert result == "<p>ok</p>"
        mock_build.assert_called_once_with(mock_request, {"hero": "h"})

    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    def test_passing_both_raises(self, mock_build, mock_templates, mock_request):
        from vibetuner.rendering import render_template_string

        with pytest.raises(TypeError, match="both 'ctx' and 'context'"):
            render_template_string(
                "partials/x.html.jinja",
                mock_request,
                {"a": 1},
                context={"b": 2},
            )


class TestContextAliasOnRenderTemplateBlock:
    @patch("vibetuner.rendering.templates")
    @patch(
        "vibetuner.rendering._build_merged_ctx",
        side_effect=lambda req, ctx: dict(ctx or {}),
    )
    def test_context_kwarg_reaches_template(
        self, mock_build, mock_templates, mock_request
    ):
        from vibetuner.rendering import render_template_block

        template_mock = MagicMock()
        template_mock.blocks = {
            "body": lambda ctx: iter(["<main>ok</main>"]),
        }
        template_mock.new_context.side_effect = lambda ctx: ctx
        mock_templates.get_template.return_value = template_mock

        render_template_block(
            "x.html.jinja", "body", mock_request, context={"hero": "h"}
        )

        mock_build.assert_called_once_with(mock_request, {"hero": "h"})

    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    def test_passing_both_raises(self, mock_build, mock_templates, mock_request):
        from vibetuner.rendering import render_template_block

        with pytest.raises(TypeError, match="both 'ctx' and 'context'"):
            render_template_block(
                "x.html.jinja",
                "body",
                mock_request,
                {"a": 1},
                context={"b": 2},
            )


class TestRenderTemplateForwardsResponseKwargs:
    """Ensure response-shaping kwargs still work after dropping **kwargs."""

    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    def test_media_type_forwarded(self, mock_build, mock_templates, mock_request):
        from vibetuner.rendering import render_template

        render_template("meta/robots.txt.jinja", mock_request, media_type="text/plain")

        _, kwargs = mock_templates.TemplateResponse.call_args
        assert kwargs["media_type"] == "text/plain"

    @patch("vibetuner.rendering.templates")
    @patch("vibetuner.rendering._build_merged_ctx", return_value={})
    def test_status_code_forwarded(self, mock_build, mock_templates, mock_request):
        from vibetuner.rendering import render_template

        render_template("x.html.jinja", mock_request, status_code=404)

        _, kwargs = mock_templates.TemplateResponse.call_args
        assert kwargs["status_code"] == 404
