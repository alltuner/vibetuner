# ABOUTME: Tests for the POST-only /auth/logout route and its GET confirmation shim.
# ABOUTME: Guards against drive-by logout via cross-origin GET (e.g. <img src=...>).
# ruff: noqa: S101
from fastapi.routing import APIRoute
from httpx import AsyncClient
from vibetuner.frontend.routes import auth as auth_routes


class TestPostLogout:
    """POST /auth/logout signs out and redirects."""

    async def test_post_returns_303_redirect_to_homepage(
        self, vibetuner_client: AsyncClient
    ):
        """POST /auth/logout redirects with 303 See Other after the side effect."""
        response = await vibetuner_client.post("/auth/logout", follow_redirects=False)

        assert response.status_code == 303
        # Homepage URL is locale-aware; the redirect target starts with /
        # and is the homepage route the framework registers.
        assert response.headers["location"].startswith("/")

    async def test_post_logout_does_not_307_preserve_method(
        self, vibetuner_client: AsyncClient
    ):
        """303 (not 307) so the browser follows with GET, not POST."""
        response = await vibetuner_client.post("/auth/logout", follow_redirects=False)

        # 307 would re-POST to the homepage; 303 correctly downgrades to GET.
        assert response.status_code != 307
        assert response.status_code == 303


class TestGetLogoutShim:
    """GET /auth/logout renders the confirmation interstitial.

    Backwards-compat: external links to the old URL still work, with
    one explicit click. Crucially, GET must NOT clear the session — that
    is the whole point of the fix.
    """

    async def test_get_renders_confirmation_form(self, vibetuner_client: AsyncClient):
        response = await vibetuner_client.get("/auth/logout")

        assert response.status_code == 200
        body = response.text
        # Form posts back to the same URL so the existing magic-link flow
        # (and any external link) lands on a real confirmation step.
        assert 'method="post"' in body
        assert "/auth/logout" in body
        assert "<button" in body and 'type="submit"' in body

    async def test_get_returns_html(self, vibetuner_client: AsyncClient):
        response = await vibetuner_client.get("/auth/logout")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")


class TestLogoutUser:
    """Direct test of the ``logout_user`` dependency that the POST runs."""

    def test_logout_user_clears_session_user(self):
        """``logout_user`` removes ``session["user"]`` if present."""
        from starlette.requests import Request

        # Build a minimal Request with a session dict the dependency can mutate.
        scope: dict = {
            "type": "http",
            "method": "POST",
            "path": "/auth/logout",
            "headers": [],
            "session": {"user": {"id": "u1", "email": "ada@example.com"}},
        }
        request = Request(scope)

        auth_routes.logout_user(request)

        assert "user" not in request.session

    def test_logout_user_is_idempotent(self):
        """Calling ``logout_user`` without a session user is not an error."""
        from starlette.requests import Request

        scope: dict = {
            "type": "http",
            "method": "POST",
            "path": "/auth/logout",
            "headers": [],
            "session": {},
        }
        request = Request(scope)

        # Must not raise.
        auth_routes.logout_user(request)

        assert "user" not in request.session


class TestRouteRegistration:
    """Lightweight checks on how the router exposes /auth/logout."""

    def test_post_logout_route_exists_and_is_named_auth_logout(self):
        """``url_for('auth_logout')`` must resolve to the POST endpoint.

        Templates render forms with ``action="{{ url_for('auth_logout') }}"``,
        and the form is what triggers the side effect — so the name must
        belong to the POST route.
        """
        post_logout = next(
            (
                r
                for r in auth_routes.router.routes
                if isinstance(r, APIRoute)
                and r.path == "/auth/logout"
                and "POST" in r.methods
            ),
            None,
        )
        assert post_logout is not None
        assert post_logout.name == "auth_logout"

    def test_get_logout_route_is_separate_shim(self):
        """The GET shim is a separate route with a distinct name."""
        get_logout = next(
            (
                r
                for r in auth_routes.router.routes
                if isinstance(r, APIRoute)
                and r.path == "/auth/logout"
                and "GET" in r.methods
            ),
            None,
        )
        assert get_logout is not None
        # url_for('auth_logout') must hit POST, not the GET shim.
        assert get_logout.name != "auth_logout"
