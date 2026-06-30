# ABOUTME: Tests that render_static_template autoescapes HTML so context data can't inject markup.
# ABOUTME: Also pins that the magic-link email templates still render their expected content.
# ruff: noqa: S101

from pathlib import Path

from vibetuner.config import HexColor
from vibetuner.templates import render_static_template


def test_html_template_escapes_context_values(tmp_path: Path) -> None:
    """User-supplied context interpolated into an HTML template is escaped,
    so a value like ``<script>`` can't break out into live markup."""
    template = tmp_path / "greeting.html.jinja"
    template.write_text("<p>Hello {{ name }}</p>")

    out = render_static_template(
        "greeting.html",
        template_path=tmp_path,
        context={"name": "<script>alert(1)</script>"},
    )

    assert "<script>alert(1)</script>" not in out
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in out


def test_non_html_template_does_not_escape(tmp_path: Path) -> None:
    """A plain-text template (``.txt``) is not HTML, so its content is emitted
    verbatim without entity escaping."""
    template = tmp_path / "note.txt.jinja"
    template.write_text("Hello {{ name }}")

    out = render_static_template(
        "note.txt",
        template_path=tmp_path,
        context={"name": "<tag> & more"},
    )

    assert out == "Hello <tag> & more"


def test_magic_link_html_email_still_renders() -> None:
    """The magic-link HTML email renders its links, button color, and copy
    intact under autoescaping (no legitimate content is mangled)."""
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

    assert 'href="https://example.com/login"' in out
    assert "background-color: #1db954" in out
    assert "Sign In" in out
    assert "expire in 15 minutes" in out


def test_magic_link_text_email_keeps_url_unescaped() -> None:
    """The plain-text magic-link email is not HTML, so a login URL with query
    separators stays as literal ``&`` rather than being entity-escaped (which
    would corrupt the link when pasted into a browser)."""
    out = render_static_template(
        "magic_link.txt",
        namespace="email",
        lang="en",
        context={
            "login_url": "https://example.com/login?token=abc&next=%2Fhome",
            "project_name": "TestApp",
        },
    )

    assert "https://example.com/login?token=abc&next=%2Fhome" in out
    assert "&amp;" not in out
    assert "Sign in to TestApp" in out
