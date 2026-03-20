# ABOUTME: Tests for OpenAPI schema visibility of routes.
# ABOUTME: Verifies framework routes are hidden and api_routes are visible in /docs.

# ruff: noqa: S101
from fastapi import APIRouter, FastAPI
from vibetuner.app_config import VibetunerApp


class TestVibetunerAppApiRoutes:
    """Tests for the api_routes field on VibetunerApp."""

    def test_api_routes_defaults_to_empty(self):
        """api_routes defaults to an empty list."""
        app = VibetunerApp()
        assert app.api_routes == []

    def test_accepts_api_routes(self):
        """VibetunerApp accepts APIRouter instances in api_routes."""
        router = APIRouter()
        app = VibetunerApp(api_routes=[router])
        assert len(app.api_routes) == 1
        assert app.api_routes[0] is router


class TestSchemaVisibility:
    """Tests that route schema visibility works correctly via include_in_schema."""

    def _get_schema_paths(self, app: FastAPI) -> set[str]:
        """Extract all paths from an app's OpenAPI schema."""
        schema = app.openapi()
        return set(schema.get("paths", {}).keys())

    def test_api_routes_appear_in_schema(self):
        """Routes registered normally appear in the OpenAPI schema."""
        app = FastAPI()
        api_router = APIRouter(prefix="/api")

        @api_router.get("/items")
        def list_items():
            return []

        app.include_router(api_router)

        paths = self._get_schema_paths(app)
        assert "/api/items" in paths

    def test_frontend_routes_hidden_from_schema(self):
        """Routes registered with include_in_schema=False are hidden."""
        app = FastAPI()
        frontend_router = APIRouter()

        @frontend_router.get("/dashboard")
        def dashboard():
            return "<html>...</html>"

        app.include_router(frontend_router, include_in_schema=False)

        paths = self._get_schema_paths(app)
        assert "/dashboard" not in paths

    def test_mixed_routes_only_api_in_schema(self):
        """When both frontend and API routes are registered, only API appears in schema."""
        app = FastAPI()

        frontend_router = APIRouter()

        @frontend_router.get("/dashboard")
        def dashboard():
            return "<html>...</html>"

        @frontend_router.get("/settings")
        def settings_page():
            return "<html>...</html>"

        api_router = APIRouter(prefix="/api")

        @api_router.get("/users")
        def list_users():
            return []

        @api_router.post("/users")
        def create_user():
            return {}

        # Frontend routes: hidden from schema
        app.include_router(frontend_router, include_in_schema=False)
        # API routes: visible in schema
        app.include_router(api_router)

        paths = self._get_schema_paths(app)
        assert "/dashboard" not in paths
        assert "/settings" not in paths
        assert "/api/users" in paths

    def test_directly_registered_routes_respect_include_in_schema(self):
        """Routes added directly on the app with include_in_schema=False are hidden."""
        app = FastAPI()

        @app.get("/static/redirect", include_in_schema=False)
        def static_redirect():
            return "redirect"

        @app.get("/api/health")
        def health():
            return {"status": "ok"}

        paths = self._get_schema_paths(app)
        assert "/static/redirect" not in paths
        assert "/api/health" in paths
