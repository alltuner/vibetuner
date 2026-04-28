# ABOUTME: Tests for BrandSettings (favicon meta, webmanifest, email button color).
# ABOUTME: Pins env-var binding, validation, fallbacks, and template rendering.
# ruff: noqa: S101

import pytest
from jinja2 import (
    ChoiceLoader,
    DictLoader,
    Environment,
    FileSystemLoader,
    select_autoescape,
)
from pydantic import ValidationError
from vibetuner.config import BrandSettings, HexColor
from vibetuner.paths import frontend_templates
from vibetuner.templates import render_static_template


# ── BrandSettings model ───────────────────────────────────────────────


class TestHexColor:
    """``HexColor`` is a ``pydantic_extra_types.color.Color`` subclass that
    pins ``str(self)`` to long-form ``#rrggbb`` hex."""

    def test_str_returns_long_hex(self):
        assert str(HexColor("#ffffff")) == "#ffffff"
        assert str(HexColor("#000000")) == "#000000"
        assert str(HexColor("#1DB954")) == "#1db954"

    def test_str_does_not_use_named_form(self):
        """Pydantic Color's default __str__ returns 'white' for #ffffff;
        HexColor pins to the hex form so HTML interpolation is predictable."""
        assert str(HexColor("white")) == "#ffffff"
        assert str(HexColor("black")) == "#000000"
        assert str(HexColor("red")) == "#ff0000"

    def test_accepts_pydantic_color_inputs(self):
        assert str(HexColor("rgb(0, 123, 255)")) == "#007bff"
        assert str(HexColor("#fff")) == "#ffffff"  # short hex expands


class TestBrandSettings:
    def test_defaults(self):
        s = BrandSettings()
        assert str(s.primary_color) == "#5b2333"
        assert str(s.browser_theme_color) == "#ffffff"
        assert s.email_button_color is None
        # email_button falls back to primary_color when override is unset
        assert str(s.email_button) == "#5b2333"

    def test_email_button_override_wins_over_primary(self):
        s = BrandSettings(primary_color="#1DB954", email_button_color="#1ED760")
        assert str(s.email_button) == "#1ed760"

    def test_email_button_falls_back_to_primary(self):
        s = BrandSettings(primary_color="#1DB954")
        assert str(s.email_button) == "#1db954"

    def test_canonicalises_to_long_lowercase_hex(self):
        s = BrandSettings(primary_color="#1DB954")
        assert str(s.primary_color) == "#1db954"

    def test_accepts_named_and_rgb_inputs(self):
        s = BrandSettings(primary_color="red", browser_theme_color="rgb(0, 0, 0)")
        assert str(s.primary_color) == "#ff0000"
        assert str(s.browser_theme_color) == "#000000"

    @pytest.mark.parametrize(
        "value",
        ["not-a-color", "rgb(", "#zzzzzz", ""],
    )
    def test_rejects_obvious_garbage(self, value: str):
        with pytest.raises(ValidationError):
            BrandSettings(primary_color=value)

    def test_env_var_binding(self, monkeypatch):
        monkeypatch.setenv("BRAND_PRIMARY_COLOR", "#1DB954")
        monkeypatch.setenv("BRAND_BROWSER_THEME_COLOR", "#191414")
        monkeypatch.setenv("BRAND_EMAIL_BUTTON_COLOR", "#1ED760")
        s = BrandSettings()
        assert str(s.primary_color) == "#1db954"
        assert str(s.browser_theme_color) == "#191414"
        assert s.email_button_color is not None
        assert str(s.email_button_color) == "#1ed760"

    def test_env_partial_uses_defaults_for_missing(self, monkeypatch):
        monkeypatch.setenv("BRAND_PRIMARY_COLOR", "#1DB954")
        s = BrandSettings()
        assert str(s.primary_color) == "#1db954"
        assert str(s.browser_theme_color) == "#ffffff"  # default
        assert str(s.email_button) == "#1db954"  # falls back to primary


# ── favicons partial render ───────────────────────────────────────────


class _StubRequest:
    class state:  # noqa: N801
        language = "en"

    url = "https://test.example.com/"


def _stub_url_for(name: str, **kwargs):
    class _URL:
        path = f"/static/{kwargs.get('path', name)}"

    return _URL()


def _make_env() -> Environment:
    from jinja2 import ChainableUndefined

    env = Environment(
        loader=ChoiceLoader(
            [
                DictLoader(
                    {
                        "child.html.jinja": (
                            "{% extends 'base/skeleton.html.jinja' %}"
                        ),
                    }
                ),
                FileSystemLoader([str(p) for p in frontend_templates]),
            ]
        ),
        autoescape=select_autoescape(["html", "jinja"]),
        undefined=ChainableUndefined,
    )
    env.globals["url_for"] = _stub_url_for
    env.globals["DEBUG"] = False
    env.globals["BODY_CLASS"] = ""
    env.globals["SKIP_HEADER"] = True
    env.globals["SKIP_FOOTER"] = True
    env.globals["project_name"] = "test"
    env.globals["project_description"] = "test"
    return env


class TestFaviconsPartial:
    def test_renders_brand_colors(self):
        env = _make_env()
        out = env.get_template("child.html.jinja").render(
            request=_StubRequest(),
            csp_nonce="n",
            umami_website_id=None,
            brand=BrandSettings(primary_color="#1DB954", browser_theme_color="#191414"),
        )
        assert 'color="#1db954"' in out  # mask-icon
        assert 'content="#1db954"' in out  # msapplication-TileColor
        assert 'content="#191414"' in out  # theme-color

    def test_renders_defaults_when_no_overrides(self):
        env = _make_env()
        out = env.get_template("child.html.jinja").render(
            request=_StubRequest(),
            csp_nonce="n",
            umami_website_id=None,
            brand=BrandSettings(),
        )
        assert 'color="#5b2333"' in out
        assert 'content="#5b2333"' in out
        assert 'content="#ffffff"' in out


# ── webmanifest + browserconfig render ────────────────────────────────


def _render_meta(name: str, brand: BrandSettings) -> str:
    """Render a meta template with url_for stubbed (production uses render_template
    which provides url_for via starlette; we mirror that here without spinning up
    a full request)."""
    env = Environment(
        loader=FileSystemLoader([str(p) for p in frontend_templates]),
        autoescape=False,  # noqa: S701 — output is JSON/XML, not HTML; matches production rendering
    )
    env.globals["url_for"] = _stub_url_for
    return env.get_template(name).render(
        project_name="TestApp", project_slug="test_app", brand=brand
    )


def test_webmanifest_uses_brand_browser_theme_color():
    out = _render_meta(
        "meta/site.webmanifest.jinja",
        BrandSettings(browser_theme_color="#191414"),
    )
    assert '"theme_color": "#191414"' in out
    assert '"background_color": "#191414"' in out


def test_browserconfig_uses_brand_primary_color():
    out = _render_meta(
        "meta/browserconfig.xml.jinja",
        BrandSettings(primary_color="#1DB954"),
    )
    assert "<TileColor>#1db954</TileColor>" in out


# ── magic-link email render ───────────────────────────────────────────


def test_magic_link_email_uses_brand_email_button():
    out = render_static_template(
        "magic_link.html",
        namespace="email",
        lang="en",
        context={
            "login_url": "https://example.com/login",
            "project_name": "TestApp",
            "button_color": HexColor("#1DB954"),
        },
    )
    assert "background-color: #1db954" in out
    # Body strings render in English (i18n via per-language template files).
    assert "Sign In" in out
    assert "expire in 15 minutes" in out


def test_magic_link_email_falls_back_to_flat_when_no_lang_match():
    """Flat-layout fallback: framework email templates ship at the namespace root,
    not under default/<lang>/, so render_static_template now falls through to
    the bare name."""
    out = render_static_template(
        "magic_link.html",
        namespace="email",
        lang="zz",  # non-existent language
        context={
            "login_url": "https://example.com/login",
            "project_name": "TestApp",
            "button_color": HexColor("#5b2333"),
        },
    )
    assert "<html>" in out
    assert "background-color: #5b2333" in out


# ── context provider wiring ──────────────────────────────────────────


def test_brand_context_provider_exposes_settings_brand():
    """The shipped _brand_context provider hands settings.brand to every render."""
    from vibetuner.rendering import _collect_provider_context

    request = _StubRequest()
    ctx = _collect_provider_context(request=request)
    assert "brand" in ctx
    assert isinstance(ctx["brand"], BrandSettings)
