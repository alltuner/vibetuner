# ABOUTME: Tests that auth endpoints carry a conservative per-IP rate limit.
# ABOUTME: Guards the magic-link send and OAuth-initiation routes against flooding.
# ruff: noqa: S101, S106

from httpx import AsyncClient


class TestAuthRateLimitSetting:
    """RateLimitSettings exposes a configurable, conservative auth limit."""

    def test_default_auth_limit(self):
        from vibetuner.config import RateLimitSettings

        assert RateLimitSettings().auth_limits == "5/minute"

    def test_auth_limit_overridable(self):
        from vibetuner.config import RateLimitSettings

        s = RateLimitSettings(auth_limits="2/minute")
        assert s.auth_limits == "2/minute"

    def test_auth_limit_from_env_var(self):
        from unittest.mock import patch

        from vibetuner.config import RateLimitSettings

        with patch.dict(
            "os.environ", {"RATE_LIMIT_AUTH_LIMITS": "9/hour"}, clear=False
        ):
            assert RateLimitSettings().auth_limits == "9/hour"


class TestMagicLinkRateLimited:
    """POST /auth/magic-link-login is throttled per client IP."""

    async def test_rapid_repeats_return_429(
        self, vibetuner_app, vibetuner_client: AsyncClient, monkeypatch
    ):
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        from vibetuner.config import settings
        from vibetuner.frontend.routes import auth as auth_routes

        # Tighten the limit so the test is fast and deterministic.
        monkeypatch.setattr(settings.rate_limit, "auth_limits", "2/minute")

        # Stub the model + email so a successful call returns 200 without Mongo
        # or a configured mail provider; the rate limit is the only thing under
        # test here.
        async def fake_create_token(email):
            return SimpleNamespace(token="tok")

        async def fake_send(**kwargs):
            return None

        monkeypatch.setattr(
            auth_routes.EmailVerificationTokenModel, "create_token", fake_create_token
        )
        monkeypatch.setattr(auth_routes, "send_magic_link_email", fake_send)
        vibetuner_app.dependency_overrides[auth_routes.get_email_service] = lambda: (
            MagicMock()
        )

        try:
            statuses = []
            for _ in range(5):
                resp = await vibetuner_client.post(
                    "/auth/magic-link-login",
                    data={"email": "flood@example.com"},
                )
                statuses.append(resp.status_code)
        finally:
            vibetuner_app.dependency_overrides.clear()

        assert 200 in statuses
        assert 429 in statuses, f"expected a 429 among {statuses}"


class TestOAuthInitRateLimited:
    """The OAuth-initiation route is decorated with the auth limit."""

    def test_oauth_login_handler_is_registered_with_limiter(self):
        # A callable limit is stored in ``limiter._dynamic_route_limits`` keyed
        # by ``module.name`` of the decorated function.
        from vibetuner.frontend.oauth import _create_auth_login_handler
        from vibetuner.ratelimit import limiter

        handler = _create_auth_login_handler("google")
        key = f"{handler.__module__}.{handler.__name__}"
        assert key in limiter._dynamic_route_limits
        assert limiter._dynamic_route_limits[key]
