# ABOUTME: Unit tests for TenantTheme model, register_tenant_theme_provider helper,
# ABOUTME: and the base/theme.html.jinja partial render.
# ruff: noqa: S101

from typing import Any
from unittest.mock import MagicMock

import pytest
from jinja2 import DictLoader, Environment, select_autoescape
from pydantic import BaseModel, Field, ValidationError
from vibetuner.models import TenantTheme
from vibetuner.paths import frontend_templates
from vibetuner.rendering import (
    _collect_provider_context,
    _context_providers,
    _template_globals,
)
from vibetuner.theming import register_tenant_theme_provider


def _reset_globals() -> None:
    _template_globals.clear()
    _context_providers.clear()


@pytest.fixture(autouse=True)
def _isolated_providers():
    _reset_globals()
    yield
    _reset_globals()


@pytest.fixture()
def request_with_tenant():
    """Build a starlette-ish request mock with arbitrary state attached."""

    def _build(**state_attrs: Any) -> MagicMock:
        request = MagicMock()
        state = MagicMock(spec=[])  # spec=[] -> no auto-attrs, raises AttributeError
        for key, value in state_attrs.items():
            setattr(state, key, value)
        request.state = state
        return request

    return _build


class TestTenantThemeModel:
    def test_default_is_empty(self):
        theme = TenantTheme()
        assert theme.overrides() == {}

    def test_overrides_includes_only_set_fields(self):
        theme = TenantTheme(primary="#009ddc", accent="#ff8800")
        assert theme.overrides() == {
            "--color-primary": "#009ddc",
            "--color-accent": "#ff8800",
        }

    def test_overrides_lowercases_hex(self):
        theme = TenantTheme(primary="#009DDC")
        assert theme.overrides() == {"--color-primary": "#009ddc"}

    def test_all_eight_role_colors(self):
        theme = TenantTheme(
            primary="#111111",
            secondary="#222222",
            accent="#333333",
            neutral="#444444",
            primary_content="#555555",
            secondary_content="#666666",
            accent_content="#777777",
            neutral_content="#888888",
        )
        assert theme.overrides() == {
            "--color-primary": "#111111",
            "--color-secondary": "#222222",
            "--color-accent": "#333333",
            "--color-neutral": "#444444",
            "--color-primary-content": "#555555",
            "--color-secondary-content": "#666666",
            "--color-accent-content": "#777777",
            "--color-neutral-content": "#888888",
        }

    @pytest.mark.parametrize(
        "bad_value",
        [
            "009ddc",  # missing #
            "#fff",  # 3-digit shorthand not allowed
            "#009ddcg",  # bad char
            "#009ddc ",  # trailing whitespace
            "rgb(0,0,0)",
            "primary",
            "",
        ],
    )
    def test_rejects_bad_hex(self, bad_value: str):
        with pytest.raises(ValidationError):
            TenantTheme(primary=bad_value)


class TestRegisterTenantThemeProvider:
    def test_no_tenant_returns_empty_context(self, request_with_tenant):
        register_tenant_theme_provider(lambda r: None)
        result = _collect_provider_context(request=request_with_tenant())
        assert "theme_overrides" not in result

    def test_tenant_without_theme_attr_returns_empty(self, request_with_tenant):
        class _Tenant:
            pass

        register_tenant_theme_provider(lambda r: _Tenant())
        result = _collect_provider_context(request=request_with_tenant())
        assert "theme_overrides" not in result

    def test_tenant_with_empty_theme_returns_empty(self, request_with_tenant):
        class _Tenant(BaseModel):
            theme: TenantTheme = Field(default_factory=TenantTheme)

        register_tenant_theme_provider(lambda r: _Tenant())
        result = _collect_provider_context(request=request_with_tenant())
        assert "theme_overrides" not in result

    def test_tenant_with_overrides_exposes_them(self, request_with_tenant):
        class _Tenant(BaseModel):
            theme: TenantTheme

        tenant = _Tenant(theme=TenantTheme(primary="#009ddc", neutral="#222222"))
        register_tenant_theme_provider(lambda r: tenant)
        result = _collect_provider_context(request=request_with_tenant())
        assert result["theme_overrides"] == {
            "--color-primary": "#009ddc",
            "--color-neutral": "#222222",
        }

    def test_custom_attribute_name(self, request_with_tenant):
        class _Tenant(BaseModel):
            branding: TenantTheme

        tenant = _Tenant(branding=TenantTheme(accent="#ff8800"))
        register_tenant_theme_provider(lambda r: tenant, attribute="branding")
        result = _collect_provider_context(request=request_with_tenant())
        assert result["theme_overrides"] == {"--color-accent": "#ff8800"}

    def test_getter_exception_is_swallowed(self, request_with_tenant, log_sink):
        def _explode(_request: Any) -> Any:
            raise RuntimeError("boom")

        register_tenant_theme_provider(_explode)
        result = _collect_provider_context(request=request_with_tenant())
        assert "theme_overrides" not in result
        assert any("getter raised" in msg for msg in log_sink)

    def test_wrong_type_on_attribute_logs_and_returns_empty(
        self, request_with_tenant, log_sink
    ):
        class _Tenant:
            theme = "not-a-theme"

        register_tenant_theme_provider(lambda r: _Tenant())
        result = _collect_provider_context(request=request_with_tenant())
        assert "theme_overrides" not in result
        assert any("expected TenantTheme" in msg for msg in log_sink)


class TestThemePartialRender:
    """Render base/theme.html.jinja directly against the framework template dir."""

    def _env(self) -> Environment:
        # Mirror the production loader so includes resolve.
        from jinja2 import FileSystemLoader

        return Environment(
            loader=FileSystemLoader([str(p) for p in frontend_templates]),
            autoescape=select_autoescape(["html", "jinja"]),
        )

    def test_no_overrides_renders_blank(self):
        env = self._env()
        template = env.get_template("base/theme.html.jinja")
        rendered = template.render(theme_overrides={}, csp_nonce="abc123")
        assert "<style" not in rendered

    def test_renders_style_block_with_nonce(self):
        env = self._env()
        template = env.get_template("base/theme.html.jinja")
        rendered = template.render(
            theme_overrides={
                "--color-primary": "#009ddc",
                "--color-accent": "#ff8800",
            },
            csp_nonce="nonce-xyz",
        )
        assert '<style nonce="nonce-xyz">' in rendered
        assert ":root {" in rendered
        assert "--color-primary: #009ddc;" in rendered
        assert "--color-accent: #ff8800;" in rendered
        assert "</style>" in rendered

    def test_html_escapes_defensively(self):
        """A caller that bypasses TenantTheme cannot inject HTML/CSS through the partial."""
        env = self._env()
        template = env.get_template("base/theme.html.jinja")
        rendered = template.render(
            theme_overrides={
                '--color-primary"</style><script>alert(1)</script>': "#000000",
            },
            csp_nonce="n",
        )
        assert "<script>alert(1)</script>" not in rendered
        assert "&lt;/style&gt;" in rendered or "&lt;script&gt;" in rendered

    def test_isolated_skeleton_includes_theme_block(self):
        """Skeleton renders the partial when ``theme_overrides`` is provided.

        Builds a tiny child template that extends a stub of the skeleton head
        section so we can inspect the include without hitting url_for or the
        i18n machinery.
        """
        env = Environment(
            loader=DictLoader(
                {
                    "skeleton_stub.html.jinja": (
                        "<head>"
                        '<link rel="stylesheet" href="bundle.css" />'
                        '{% include "base/theme.html.jinja" %}'
                        "</head>"
                    ),
                }
            ),
            autoescape=select_autoescape(["html", "jinja"]),
        )
        # Splice the framework partial into the env loader.
        from jinja2 import ChoiceLoader, FileSystemLoader

        env.loader = ChoiceLoader(
            [
                env.loader,
                FileSystemLoader([str(p) for p in frontend_templates]),
            ]
        )
        rendered = env.get_template("skeleton_stub.html.jinja").render(
            theme_overrides={"--color-primary": "#009ddc"},
            csp_nonce="N",
        )
        # Cascade order: theme block must appear *after* the bundle.css link.
        link_index = rendered.index('href="bundle.css"')
        style_index = rendered.index("<style")
        assert link_index < style_index
