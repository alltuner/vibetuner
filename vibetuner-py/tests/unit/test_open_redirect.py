# ABOUTME: Route-level tests that post-auth redirect targets reject open-redirect payloads.
# ABOUTME: Covers email_verify, OAuth next_url stashing, and the set-language route.
# ruff: noqa: S101, S106

from httpx import AsyncClient


class TestSetLanguageRedirect:
    """GET /set-language/{lang} must not redirect off-site via ``current``."""

    async def test_safe_current_path_is_preserved(self, vibetuner_client: AsyncClient):
        resp = await vibetuner_client.get(
            "/set-language/en", params={"current": "/dashboard"}, follow_redirects=False
        )
        assert resp.status_code in (302, 307)
        assert resp.headers["location"] == "/en/dashboard"

    async def test_absolute_url_falls_back_to_homepage(
        self, vibetuner_client: AsyncClient
    ):
        resp = await vibetuner_client.get(
            "/set-language/en",
            params={"current": "https://evil.com"},
            follow_redirects=False,
        )
        location = resp.headers["location"]
        assert "evil.com" not in location
        assert location.startswith("/")

    async def test_protocol_relative_url_falls_back_to_homepage(
        self, vibetuner_client: AsyncClient
    ):
        resp = await vibetuner_client.get(
            "/set-language/en",
            params={"current": "//evil.com"},
            follow_redirects=False,
        )
        location = resp.headers["location"]
        assert "evil.com" not in location
        assert location.startswith("/")


class TestOAuthNextStash:
    """``_create_auth_login_handler`` only stashes a same-origin ``next``.

    The handler short-circuits via a stubbed ``resolve_oauth_client`` that
    raises ``ValueError`` right after the ``next`` stash, so Authlib and
    ``url_for`` are never reached.
    """

    async def test_unsafe_next_is_not_stashed(self, monkeypatch):
        from vibetuner.frontend import oauth as oauth_mod
        from vibetuner.ratelimit import limiter

        # The handler is rate-limited; disable limiting so this redirect-only
        # assertion is independent of per-IP counters shared across the suite.
        monkeypatch.setattr(limiter, "enabled", False)

        captured: dict = {}

        async def fake_resolve(provider_name, app_id):
            # Raise to short-circuit after the stash so we never touch Authlib.
            raise ValueError("stop")

        def fake_homepage(request, path_only=True):
            return "/en/"

        monkeypatch.setattr(oauth_mod, "resolve_oauth_client", fake_resolve)
        monkeypatch.setattr(oauth_mod, "get_homepage_url", fake_homepage)

        from starlette.requests import Request

        scope: dict = {
            "type": "http",
            "method": "GET",
            "path": "/auth/login/provider/google",
            "headers": [],
            "session": captured,
            "state": {"language": "en"},
        }
        request = Request(scope)

        handler = oauth_mod._create_auth_login_handler("google")
        await handler(request, next="https://evil.com")

        assert captured["next_url"] == "/en/"

    async def test_safe_next_is_stashed(self, monkeypatch):
        from vibetuner.frontend import oauth as oauth_mod
        from vibetuner.ratelimit import limiter

        monkeypatch.setattr(limiter, "enabled", False)

        async def fake_resolve(provider_name, app_id):
            raise ValueError("stop")

        def fake_homepage(request, path_only=True):
            return "/en/"

        monkeypatch.setattr(oauth_mod, "resolve_oauth_client", fake_resolve)
        monkeypatch.setattr(oauth_mod, "get_homepage_url", fake_homepage)

        from starlette.requests import Request

        captured: dict = {}
        scope: dict = {
            "type": "http",
            "method": "GET",
            "path": "/auth/login/provider/google",
            "headers": [],
            "session": captured,
            "state": {"language": "en"},
        }
        request = Request(scope)

        handler = oauth_mod._create_auth_login_handler("google")
        await handler(request, next="/dashboard")

        assert captured["next_url"] == "/dashboard"


class TestEmailVerifyRedirect:
    """``email_verify`` only honors a same-origin ``next``.

    The model lookups (token verification, user load/create) and the session
    write are not under test here, so they are stubbed: this isolates the
    redirect-target decision, which is the open-redirect fix.
    """

    def _request(self):
        from starlette.requests import Request

        scope: dict = {
            "type": "http",
            "method": "GET",
            "path": "/auth/email-verify/tok",
            "headers": [],
            "session": {},
            "state": {"language": "en"},
        }
        return Request(scope)

    async def _verify(self, monkeypatch, next_value):
        from types import SimpleNamespace

        from vibetuner.frontend.routes import auth as auth_routes

        async def fake_verify_token(token):
            return SimpleNamespace(email="alice@example.com")

        async def fake_get_by_email(email):
            return SimpleNamespace(session_dict={"id": "u1", "email": email})

        monkeypatch.setattr(
            auth_routes.EmailVerificationTokenModel,
            "verify_token",
            fake_verify_token,
        )
        monkeypatch.setattr(auth_routes.UserModel, "get_by_email", fake_get_by_email)
        monkeypatch.setattr(auth_routes, "get_homepage_url", lambda request: "/en/")

        return await auth_routes.email_verify(
            self._request(), token="tok", next=next_value
        )

    async def test_unsafe_next_falls_back_to_homepage(self, monkeypatch):
        result = await self._verify(monkeypatch, "https://evil.com")
        assert result == "/en/"

    async def test_protocol_relative_next_falls_back_to_homepage(self, monkeypatch):
        result = await self._verify(monkeypatch, "//evil.com")
        assert result == "/en/"

    async def test_safe_next_is_honored(self, monkeypatch):
        result = await self._verify(monkeypatch, "/dashboard")
        assert result == "/dashboard"
