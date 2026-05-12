# ABOUTME: Tests for the OAuth relay state-wrapping helper.
# ABOUTME: Verifies that the relay return URL is derived correctly from the request.
# ruff: noqa: S101
from urllib.parse import parse_qs, urlparse

from starlette.requests import Request
from vibetuner.frontend.oauth import (
    _public_origin_for_relay,
    _wrap_oauth_relay_state,
)


def _request(scheme: str, host_header: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "scheme": scheme,
        "path": "/auth/google",
        "raw_path": b"/auth/google",
        "query_string": b"",
        "headers": [(b"host", host_header.encode("latin-1"))],
        "server": (host_header.split(":")[0], None),
        "client": ("127.0.0.1", 12345),
        "root_path": "",
    }
    return Request(scope)


class TestWrapOauthRelayState:
    """Tests for _wrap_oauth_relay_state()."""

    def test_prefixes_state_with_public_origin(self):
        location = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            "?response_type=code"
            "&client_id=abc"
            "&state=opaque-token"
            "&redirect_uri=https://relay.example.com/auth/provider/google"
        )

        wrapped = _wrap_oauth_relay_state(location, "https://app.tunnel.example.com")

        params = parse_qs(urlparse(wrapped).query)
        assert params["state"] == ["https://app.tunnel.example.com|opaque-token"]

    def test_preserves_other_query_params(self):
        location = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            "?response_type=code"
            "&client_id=abc"
            "&state=opaque-token"
            "&scope=openid+email"
        )

        wrapped = _wrap_oauth_relay_state(location, "https://app.example.com")

        params = parse_qs(urlparse(wrapped).query)
        assert params["response_type"] == ["code"]
        assert params["client_id"] == ["abc"]
        assert params["scope"] == ["openid email"]

    def test_returns_location_unchanged_when_no_state_param(self):
        location = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code"

        wrapped = _wrap_oauth_relay_state(location, "https://app.example.com")

        assert wrapped == location

    def test_handles_localhost_origin(self):
        location = "https://accounts.google.com/o/oauth2/v2/auth?state=opaque-token"

        wrapped = _wrap_oauth_relay_state(location, "http://localhost:28000")

        params = parse_qs(urlparse(wrapped).query)
        assert params["state"] == ["http://localhost:28000|opaque-token"]


class TestPublicOriginForRelay:
    """Tests for _public_origin_for_relay()."""

    def test_forces_https_for_public_tunnel_host(self):
        # frpc/ngrok/cloudflare deliver the request as plain http internally,
        # but the public edge is always TLS; the state must reflect https.
        request = _request("http", "sturdy-ferret-f5df.lab.alltuner.com")

        assert (
            _public_origin_for_relay(request)
            == "https://sturdy-ferret-f5df.lab.alltuner.com"
        )

    def test_forces_https_even_when_host_has_port(self):
        request = _request("http", "app.tunnel.example.com:8443")

        assert (
            _public_origin_for_relay(request) == "https://app.tunnel.example.com:8443"
        )

    def test_keeps_http_for_localhost(self):
        request = _request("http", "localhost:8000")

        assert _public_origin_for_relay(request) == "http://localhost:8000"

    def test_keeps_http_for_loopback_ipv4(self):
        request = _request("http", "127.0.0.1:8000")

        assert _public_origin_for_relay(request) == "http://127.0.0.1:8000"

    def test_keeps_http_for_loopback_ipv6(self):
        request = _request("http", "[::1]:8000")

        assert _public_origin_for_relay(request) == "http://[::1]:8000"
