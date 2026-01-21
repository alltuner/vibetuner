# ABOUTME: Unit tests for LocalizedRouter class
# ABOUTME: Verifies router-level localization control for SEO routes
# ruff: noqa: S101

from fastapi import APIRouter


class LocalizedRouter(APIRouter):
    """Test copy of router to avoid importing full vibetuner.frontend package.

    Mirrors the implementation in vibetuner.frontend.routing.LocalizedRouter.
    """

    def __init__(self, *args, localized: bool | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._localized = localized

    def add_api_route(self, path, endpoint, **kwargs):
        if not hasattr(endpoint, "_localized"):
            if self._localized is not None:
                endpoint._localized = self._localized
        return super().add_api_route(path, endpoint, **kwargs)


class TestLocalizedRouter:
    """Test LocalizedRouter class."""

    def test_explicit_localized_true_marks_endpoints(self):
        """Router with localized=True marks all endpoints as localized."""
        router = LocalizedRouter(localized=True)

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert hasattr(my_endpoint, "_localized")
        assert my_endpoint._localized is True

    def test_explicit_localized_false_marks_endpoints(self):
        """Router with localized=False marks all endpoints as non-localized."""
        router = LocalizedRouter(localized=False)

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert hasattr(my_endpoint, "_localized")
        assert my_endpoint._localized is False

    def test_localized_none_does_not_mark_endpoints(self):
        """Router with localized=None does not mark endpoints."""
        router = LocalizedRouter(localized=None)

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert not hasattr(my_endpoint, "_localized")

    def test_default_is_none(self):
        """Router without localized argument defaults to None."""
        router = LocalizedRouter()

        async def my_endpoint():
            pass

        router.add_api_route("/test", my_endpoint)

        assert not hasattr(my_endpoint, "_localized")

    def test_does_not_override_existing_localized_attribute(self):
        """Router does not override endpoint's existing _localized attribute."""
        router = LocalizedRouter(localized=True)

        async def my_endpoint():
            pass

        my_endpoint._localized = False  # Preset

        router.add_api_route("/test", my_endpoint)

        assert my_endpoint._localized is False  # Should remain unchanged

    def test_multiple_endpoints_same_router(self):
        """Multiple endpoints on same router all get same localized setting."""
        router = LocalizedRouter(localized=True)

        async def endpoint_a():
            pass

        async def endpoint_b():
            pass

        router.add_api_route("/a", endpoint_a)
        router.add_api_route("/b", endpoint_b)

        assert endpoint_a._localized is True
        assert endpoint_b._localized is True

    def test_inherits_apirouter_features(self):
        """LocalizedRouter inherits all APIRouter features."""
        router = LocalizedRouter(prefix="/api", tags=["test"], localized=True)

        assert router.prefix == "/api"
        assert router.tags == ["test"]

    def test_decorator_style_routes(self):
        """Decorator-style routes work correctly."""
        router = LocalizedRouter(localized=True)

        @router.get("/test")
        async def my_endpoint():
            pass

        assert hasattr(my_endpoint, "_localized")
        assert my_endpoint._localized is True
