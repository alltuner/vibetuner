# ABOUTME: Unit tests for vibetuner.config module
# ABOUTME: Tests environment configuration and redis_key_prefix computation
# ruff: noqa: S101

from unittest.mock import patch

import pytest
from vibetuner.config import CoreConfiguration, ProjectConfiguration


class TestCoreConfigurationEnvironment:
    """Test environment configuration in CoreConfiguration."""

    def test_environment_default_is_dev(self):
        """Test that environment defaults to 'dev'."""
        with patch.dict("os.environ", {}, clear=True):
            config = CoreConfiguration(project=ProjectConfiguration())
            assert config.environment == "dev"

    def test_environment_from_env_var(self):
        """Test that environment can be set via ENVIRONMENT env var."""
        with patch.dict("os.environ", {"ENVIRONMENT": "prod"}, clear=False):
            config = CoreConfiguration(project=ProjectConfiguration())
            assert config.environment == "prod"

    def test_environment_validation(self):
        """Test that environment only accepts 'dev' or 'prod'."""
        with pytest.raises(ValueError):
            CoreConfiguration(project=ProjectConfiguration(), environment="invalid")


class TestRedisKeyPrefix:
    """Test redis_key_prefix computed property."""

    def test_redis_key_prefix_dev_environment(self):
        """Test redis_key_prefix format for dev environment."""
        project = ProjectConfiguration(project_slug="myproject")
        config = CoreConfiguration(project=project, environment="dev")
        assert config.redis_key_prefix == "myproject:dev:"

    def test_redis_key_prefix_prod_environment(self):
        """Test redis_key_prefix format for prod environment."""
        project = ProjectConfiguration(project_slug="myproject")
        config = CoreConfiguration(project=project, environment="prod")
        assert config.redis_key_prefix == "myproject:"

    def test_redis_key_prefix_with_different_slugs(self):
        """Test redis_key_prefix with different project slugs."""
        test_cases = [
            ("simple", "dev", "simple:dev:"),
            ("my_project", "dev", "my_project:dev:"),
            ("app123", "prod", "app123:"),
            ("test-app", "prod", "test-app:"),
        ]

        for slug, env, expected in test_cases:
            project = ProjectConfiguration(project_slug=slug)
            config = CoreConfiguration(project=project, environment=env)
            assert config.redis_key_prefix == expected, (
                f"Failed for slug={slug}, env={env}"
            )


class TestWorkerConcurrency:
    """Test worker_concurrency configuration."""

    def test_worker_concurrency_default_is_16(self):
        """Test that worker_concurrency defaults to 16."""
        config = CoreConfiguration(project=ProjectConfiguration())
        assert config.worker_concurrency == 16

    def test_worker_concurrency_from_env_var(self):
        """Test that worker_concurrency can be set via WORKER_CONCURRENCY env var."""
        with patch.dict("os.environ", {"WORKER_CONCURRENCY": "64"}, clear=False):
            config = CoreConfiguration(project=ProjectConfiguration())
            assert config.worker_concurrency == 64

    def test_worker_concurrency_constructor_override(self):
        """Test that worker_concurrency can be set via constructor."""
        config = CoreConfiguration(
            project=ProjectConfiguration(), worker_concurrency=128
        )
        assert config.worker_concurrency == 128
