# ABOUTME: Tests for the app configuration loader.
# ABOUTME: Verifies tune.py loading, error handling, and zero-config behavior.
# ruff: noqa: S101
from types import ModuleType
from unittest.mock import patch

import pytest
from vibetuner.app_config import VibetunerApp
from vibetuner.loader import ConfigurationError, load_app_config


@pytest.fixture(autouse=True)
def clear_loader_cache():
    """Clear the lru_cache before and after each test."""
    load_app_config.cache_clear()
    yield
    load_app_config.cache_clear()


class TestLoadAppConfig:
    """Tests for load_app_config function."""

    def test_returns_default_when_no_project_name(self):
        """When not in a project directory, returns empty VibetunerApp."""
        with patch("vibetuner.loader.get_project_name", return_value=None):
            config = load_app_config()

        assert isinstance(config, VibetunerApp)
        assert config.models == []
        assert config.routes == []

    def test_returns_default_when_no_tune_py(self):
        """When tune.py doesn't exist, returns empty VibetunerApp (zero-config)."""
        with (
            patch("vibetuner.loader.get_project_name", return_value="myapp"),
            patch(
                "vibetuner.loader.import_module",
                side_effect=ModuleNotFoundError(name="myapp.tune"),
            ),
        ):
            config = load_app_config()

        assert isinstance(config, VibetunerApp)
        assert config.models == []

    def test_loads_valid_tune_py(self):
        """When tune.py exists with valid app, loads it."""

        class FakeModel:
            pass

        mock_app = VibetunerApp(models=[FakeModel])

        mock_module = ModuleType("myapp.tune")
        mock_module.app = mock_app

        with (
            patch("vibetuner.loader.get_project_name", return_value="myapp"),
            patch("vibetuner.loader.import_module", return_value=mock_module),
        ):
            config = load_app_config()

        assert config is mock_app
        assert len(config.models) == 1

    def test_raises_when_no_app_export(self):
        """When tune.py exists but has no 'app', raises ConfigurationError."""
        mock_module = ModuleType("myapp.tune")
        # No 'app' attribute

        with (
            patch("vibetuner.loader.get_project_name", return_value="myapp"),
            patch("vibetuner.loader.import_module", return_value=mock_module),
            pytest.raises(ConfigurationError) as exc_info,
        ):
            load_app_config()

        assert "must export an 'app' object" in str(exc_info.value)

    def test_raises_when_app_wrong_type(self):
        """When tune.py exports wrong type, raises ConfigurationError."""
        mock_module = ModuleType("myapp.tune")
        mock_module.app = {"not": "a VibetunerApp"}

        with (
            patch("vibetuner.loader.get_project_name", return_value="myapp"),
            patch("vibetuner.loader.import_module", return_value=mock_module),
            pytest.raises(ConfigurationError) as exc_info,
        ):
            load_app_config()

        assert "must be a VibetunerApp instance" in str(exc_info.value)

    def test_surfaces_import_errors_in_tune_py(self):
        """When tune.py has import errors, surfaces them (doesn't mask)."""
        # Simulate an import error inside tune.py (not tune.py itself missing)
        error = ModuleNotFoundError("No module named 'nonexistent_package'")
        error.name = "nonexistent_package"

        with (
            patch("vibetuner.loader.get_project_name", return_value="myapp"),
            patch("vibetuner.loader.import_module", side_effect=error),
            pytest.raises(ModuleNotFoundError) as exc_info,
        ):
            load_app_config()

        assert "nonexistent_package" in str(exc_info.value)

    def test_lru_cache_behavior(self):
        """Verifies load_app_config is cached."""
        mock_app = VibetunerApp()
        mock_module = ModuleType("myapp.tune")
        mock_module.app = mock_app

        with (
            patch("vibetuner.loader.get_project_name", return_value="myapp"),
            patch(
                "vibetuner.loader.import_module", return_value=mock_module
            ) as mock_import,
        ):
            config1 = load_app_config()
            config2 = load_app_config()

        assert config1 is config2
        # import_module should only be called once due to caching
        assert mock_import.call_count == 1


class TestVibetunerApp:
    """Tests for VibetunerApp Pydantic model."""

    def test_default_values(self):
        """VibetunerApp has sensible defaults."""
        app = VibetunerApp()

        assert app.models == []
        assert app.routes == []
        assert app.middleware == []
        assert app.template_filters == {}
        assert app.frontend_lifespan is None
        assert app.oauth_providers == []
        assert app.tasks == []
        assert app.worker_lifespan is None
        assert app.cli is None

    def test_accepts_models(self):
        """VibetunerApp accepts model classes."""

        class FakeModel:
            pass

        app = VibetunerApp(models=[FakeModel])

        assert len(app.models) == 1
        assert app.models[0] is FakeModel

    def test_accepts_routes(self):
        """VibetunerApp accepts APIRouter instances."""
        from fastapi import APIRouter

        router = APIRouter()
        app = VibetunerApp(routes=[router])

        assert len(app.routes) == 1
        assert app.routes[0] is router

    def test_accepts_middleware(self):
        """VibetunerApp accepts Middleware instances."""
        from starlette.middleware import Middleware
        from starlette.middleware.base import BaseHTTPMiddleware

        mw = Middleware(BaseHTTPMiddleware)
        app = VibetunerApp(middleware=[mw])

        assert len(app.middleware) == 1

    def test_accepts_template_filters(self):
        """VibetunerApp accepts template filter functions."""

        def my_filter(value: str) -> str:
            return value.upper()

        app = VibetunerApp(template_filters={"upper": my_filter})

        assert "upper" in app.template_filters
        assert app.template_filters["upper"]("hello") == "HELLO"

    def test_accepts_lifespan(self):
        """VibetunerApp accepts lifespan context managers."""
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def my_lifespan(app):
            yield

        app = VibetunerApp(frontend_lifespan=my_lifespan)

        assert app.frontend_lifespan is my_lifespan

    def test_accepts_oauth_providers(self):
        """VibetunerApp accepts OAuth provider names."""
        app = VibetunerApp(oauth_providers=["google", "github"])

        assert app.oauth_providers == ["google", "github"]

    def test_accepts_tasks(self):
        """VibetunerApp accepts task functions."""

        async def my_task():
            pass

        app = VibetunerApp(tasks=[my_task])

        assert len(app.tasks) == 1
        assert app.tasks[0] is my_task

    def test_accepts_cli(self):
        """VibetunerApp accepts Typer CLI app."""
        import typer

        cli = typer.Typer()
        app = VibetunerApp(cli=cli)

        assert app.cli is cli
