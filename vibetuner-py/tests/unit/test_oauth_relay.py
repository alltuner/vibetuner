# ABOUTME: Tests for the OAuth relay state-wrapping helper.
# ABOUTME: Verifies that the relay return URL is derived correctly from the request.
# ruff: noqa: S101
from urllib.parse import parse_qs, urlparse

from vibetuner.frontend.oauth import _wrap_oauth_relay_state


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

        wrapped = _wrap_oauth_relay_state(
            location, "https://app.tunnel.example.com"
        )

        params = parse_qs(urlparse(wrapped).query)
        assert params["state"] == [
            "https://app.tunnel.example.com|opaque-token"
        ]

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
        location = (
            "https://accounts.google.com/o/oauth2/v2/auth?state=opaque-token"
        )

        wrapped = _wrap_oauth_relay_state(location, "http://localhost:28000")

        params = parse_qs(urlparse(wrapped).query)
        assert params["state"] == ["http://localhost:28000|opaque-token"]
