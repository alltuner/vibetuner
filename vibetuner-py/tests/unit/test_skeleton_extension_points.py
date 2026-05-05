# ABOUTME: Tests for skeleton.html.jinja extension blocks and context vars.
# ABOUTME: Pins behavior so projects can extend instead of wholesale-overriding.
# ruff: noqa: S101, N801

from typing import Any

import pytest
from jinja2 import (
    ChainableUndefined,
    ChoiceLoader,
    DictLoader,
    Environment,
    FileSystemLoader,
    select_autoescape,
)
from vibetuner.paths import frontend_templates


# A minimal harness: render a tiny child template that extends the framework
# skeleton, with framework-side includes resolvable via FileSystemLoader.
# Skeleton-included partials (opengraph, favicons) reference globals like
# ``project_name`` that aren't relevant to these tests; ChainableUndefined
# silently renders missing chains as empty so we don't have to stub them all.


class _StubRequest:
    class state:
        language = "en"

    url = "https://test.example.com/"


def _stub_url_for(name: str, **kwargs: Any) -> Any:
    class _URL:
        path = f"/static/{kwargs.get('path', name)}"

    return _URL()


def _make_env(child_body: str = "") -> Environment:
    env = Environment(
        loader=ChoiceLoader(
            [
                DictLoader(
                    {
                        "_test_child.html.jinja": (
                            "{% extends 'base/skeleton.html.jinja' %}" + child_body
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


def _render(env: Environment, **ctx: Any) -> str:
    base = {"request": _StubRequest(), "csp_nonce": "n", "umami_website_id": None}
    base.update(ctx)
    return env.get_template("_test_child.html.jinja").render(**base)


# ── color_scheme context var ──────────────────────────────────────────


class TestColorScheme:
    def test_defaults_to_light(self):
        out = _render(_make_env())
        assert '<meta name="color-scheme" content="light" />' in out

    def test_can_be_overridden(self):
        out = _render(_make_env(), color_scheme="dark")
        assert '<meta name="color-scheme" content="dark" />' in out

    def test_value_is_html_escaped(self):
        out = _render(_make_env(), color_scheme='"><script>alert(1)</script>')
        assert "<script>alert(1)</script>" not in out


# ── canonical_url context var ─────────────────────────────────────────


class TestCanonicalUrl:
    def test_omitted_when_unset(self):
        out = _render(_make_env())
        assert 'rel="canonical"' not in out

    def test_renders_when_set(self):
        out = _render(_make_env(), canonical_url="https://example.com/post/42")
        assert '<link rel="canonical" href="https://example.com/post/42" />' in out

    def test_value_is_html_escaped(self):
        out = _render(
            _make_env(),
            canonical_url='https://x"><script>alert(1)</script>',
        )
        assert "<script>alert(1)</script>" not in out


# ── font_preloads context var ─────────────────────────────────────────


class TestFontPreloads:
    def test_omitted_when_unset(self):
        out = _render(_make_env())
        assert 'rel="preload"' not in out

    def test_renders_each_entry(self):
        out = _render(
            _make_env(),
            font_preloads=[
                {
                    "href": "/fonts/brand.woff2",
                    "type": "font/woff2",
                    "crossorigin": "anonymous",
                },
                {
                    "href": "/fonts/mono.woff2",
                    "type": "font/woff2",
                },
            ],
        )
        # djlint may reformat the <link> tag onto multiple lines, so collapse
        # whitespace before checking that all expected attributes appear in
        # one tag.
        flat = " ".join(out.split())
        assert 'rel="preload" as="font" href="/fonts/brand.woff2"' in flat
        assert 'href="/fonts/brand.woff2"' in flat
        assert 'type="font/woff2"' in flat
        assert 'crossorigin="anonymous"' in flat
        assert 'href="/fonts/mono.woff2"' in flat

    def test_crossorigin_omitted_when_falsy(self):
        out = _render(
            _make_env(),
            font_preloads=[{"href": "/f.woff2", "type": "font/woff2"}],
        )
        assert "crossorigin=" not in out


# ── extension blocks ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "block,marker",
    [
        ("extra_head_links", "<!-- HEADLINK -->"),
        ("extra_scripts", "<!-- SCRIPT -->"),
        ("before_main", "<!-- BEFORE -->"),
        ("after_main", "<!-- AFTER -->"),
    ],
)
def test_extension_block_renders_when_overridden(block: str, marker: str):
    """Each new block accepts content from a child template."""
    env = _make_env(child_body=f"{{% block {block} %}}{marker}{{% endblock {block} %}}")
    rendered = _render(env)
    assert marker in rendered


def test_extension_blocks_empty_by_default():
    """No new block renders any content when not overridden."""
    out = _render(_make_env())
    # There should be no stray HTML comments leaking from the new blocks.
    for marker in (
        "<!-- HEADLINK -->",
        "<!-- SCRIPT -->",
        "<!-- BEFORE -->",
        "<!-- AFTER -->",
    ):
        assert marker not in out


# ── cascade-order invariants ─────────────────────────────────────────


def test_canonical_and_font_preloads_render_before_bundle_css():
    """Preload scanner needs <link rel="preload"> before the stylesheet."""
    out = _render(
        _make_env(),
        canonical_url="https://example.com/",
        font_preloads=[{"href": "/f.woff2", "type": "font/woff2"}],
    )
    css_idx = out.index("bundle.css")
    canonical_idx = out.index('rel="canonical"')
    preload_idx = out.index('rel="preload"')
    assert canonical_idx < css_idx
    assert preload_idx < css_idx


def test_extra_head_links_block_renders_before_bundle_css():
    env = _make_env(
        child_body=(
            "{% block extra_head_links %}<!-- EXTRAS -->{% endblock extra_head_links %}"
        )
    )
    out = _render(env)
    assert out.index("<!-- EXTRAS -->") < out.index("bundle.css")


def test_extra_scripts_block_renders_after_bundle_js():
    env = _make_env(
        child_body=(
            "{% block extra_scripts %}<!-- AFTER_BUNDLE -->{% endblock extra_scripts %}"
        )
    )
    out = _render(env)
    assert out.index("bundle.js") < out.index("<!-- AFTER_BUNDLE -->")


def test_before_main_and_after_main_wrap_body():
    """before_main precedes the body block; after_main follows it."""
    env = _make_env(
        child_body=(
            "{% block before_main %}<!-- PRE -->{% endblock before_main %}"
            "{% block content %}<!-- BODY -->{% endblock content %}"
            "{% block after_main %}<!-- POST -->{% endblock after_main %}"
        )
    )
    out = _render(env)
    pre = out.index("<!-- PRE -->")
    body = out.index("<!-- BODY -->")
    post = out.index("<!-- POST -->")
    assert pre < body < post


# ── scrollbar gutter ─────────────────────────────────────────────────


class TestScrollbarGutter:
    def test_emits_stable_gutter_rule(self):
        out = _render(_make_env())
        compact = "".join(out.split())
        assert "html{scrollbar-gutter:stable" in compact

    def test_uses_csp_nonce(self):
        out = _render(_make_env())
        # The inline <style> for the gutter rule must carry the nonce so it
        # passes the CSP style-src directive.
        assert 'nonce="n"' in out
        # Locate the gutter rule and check the nearest preceding <style> tag
        # carries a nonce attribute.
        gutter_idx = out.index("scrollbar-gutter")
        style_open = out.rfind("<style", 0, gutter_idx)
        assert style_open != -1
        style_close = out.index(">", style_open)
        assert "nonce=" in out[style_open:style_close]

    def test_renders_before_bundle_css(self):
        """Inline gutter rule must precede bundle.css so the user bundle wins
        the cascade if a project chooses to override it."""
        out = _render(_make_env())
        assert out.index("scrollbar-gutter") < out.index("bundle.css")
