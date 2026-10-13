# ABOUTME: Renders the core /sitemap.xml template through the real meta route.
# ABOUTME: Checks hreflang alternates for multi-language apps and unchanged single-language output.

# ruff: noqa: S101
from xml.etree.ElementTree import Element, fromstring

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from vibetuner.context import ctx
from vibetuner.frontend.routes import meta


SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"


def _get_sitemap(
    monkeypatch: pytest.MonkeyPatch, languages: set[str], default_language: str
) -> bytes:
    monkeypatch.setattr(ctx, "fqdn", "example.com")
    monkeypatch.setattr(ctx, "supported_languages", languages)
    monkeypatch.setattr(ctx, "default_language", default_language)
    app = FastAPI()
    app.include_router(meta.router)

    response = TestClient(app).get("/sitemap.xml")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    return response.content


def _alternates(url: Element) -> dict[str, str]:
    return {
        link.attrib["hreflang"]: link.attrib["href"]
        for link in url.findall(f"{{{XHTML_NS}}}link")
        if link.attrib["rel"] == "alternate"
    }


def test_single_language_sitemap_has_no_alternates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = _get_sitemap(monkeypatch, {"en"}, "en")

    assert content == (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        b"    <url>\n"
        b"        <loc>https://example.com/</loc>\n"
        b"    </url>\n"
        b"</urlset>"
    )


def test_multi_language_sitemap_lists_hreflang_alternates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = _get_sitemap(monkeypatch, {"es", "en", "ca"}, "en")

    # Parses the framework's own output, not untrusted input.
    root = fromstring(content)  # noqa: S314
    urls = root.findall(f"{{{SITEMAP_NS}}}url")
    locs = [url.findtext(f"{{{SITEMAP_NS}}}loc") for url in urls]
    assert locs == [
        "https://example.com/",
        "https://example.com/ca/",
        "https://example.com/en/",
        "https://example.com/es/",
    ]
    expected = {
        "ca": "https://example.com/ca/",
        "en": "https://example.com/en/",
        "es": "https://example.com/es/",
        "x-default": "https://example.com/",
    }
    for url in urls:
        assert _alternates(url) == expected
