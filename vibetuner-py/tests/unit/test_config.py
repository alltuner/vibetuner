# ABOUTME: Unit tests for vibetuner.config module
# ABOUTME: Tests environment configuration, locale detection, and redis_key_prefix computation
# ruff: noqa: S101

from unittest.mock import patch

import pytest
from vibetuner.config import (
    CoreConfiguration,
    LocaleDetectionSettings,
    ProjectConfiguration,
)


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


class TestLocaleDetectionSettings:
    """Test LocaleDetectionSettings configuration."""

    def test_all_selectors_enabled_by_default(self):
        """Test that all locale selectors are enabled by default."""
        settings = LocaleDetectionSettings()
        assert settings.query_param is True
        assert settings.url_prefix is True
        assert settings.user_session is True
        assert settings.cookie is True
        assert settings.accept_language is True

    def test_query_param_from_env_var(self):
        """Test that query_param can be disabled via LOCALE_QUERY_PARAM env var."""
        with patch.dict("os.environ", {"LOCALE_QUERY_PARAM": "false"}, clear=False):
            settings = LocaleDetectionSettings()
            assert settings.query_param is False

    def test_url_prefix_from_env_var(self):
        """Test that url_prefix can be disabled via LOCALE_URL_PREFIX env var."""
        with patch.dict("os.environ", {"LOCALE_URL_PREFIX": "false"}, clear=False):
            settings = LocaleDetectionSettings()
            assert settings.url_prefix is False

    def test_user_session_from_env_var(self):
        """Test that user_session can be disabled via LOCALE_USER_SESSION env var."""
        with patch.dict("os.environ", {"LOCALE_USER_SESSION": "false"}, clear=False):
            settings = LocaleDetectionSettings()
            assert settings.user_session is False

    def test_cookie_from_env_var(self):
        """Test that cookie can be disabled via LOCALE_COOKIE env var."""
        with patch.dict("os.environ", {"LOCALE_COOKIE": "false"}, clear=False):
            settings = LocaleDetectionSettings()
            assert settings.cookie is False

    def test_accept_language_from_env_var(self):
        """Test that accept_language can be disabled via LOCALE_ACCEPT_LANGUAGE env var."""
        with patch.dict("os.environ", {"LOCALE_ACCEPT_LANGUAGE": "false"}, clear=False):
            settings = LocaleDetectionSettings()
            assert settings.accept_language is False

    def test_multiple_selectors_disabled(self):
        """Test that multiple selectors can be disabled simultaneously."""
        env_vars = {
            "LOCALE_QUERY_PARAM": "false",
            "LOCALE_USER_SESSION": "false",
            "LOCALE_ACCEPT_LANGUAGE": "false",
        }
        with patch.dict("os.environ", env_vars, clear=False):
            settings = LocaleDetectionSettings()
            assert settings.query_param is False
            assert settings.url_prefix is True
            assert settings.user_session is False
            assert settings.cookie is True
            assert settings.accept_language is False

    def test_case_insensitive_env_var(self):
        """Test that env var values are case insensitive."""
        with patch.dict("os.environ", {"LOCALE_QUERY_PARAM": "False"}, clear=False):
            settings = LocaleDetectionSettings()
            assert settings.query_param is False

    def test_constructor_override(self):
        """Test that selectors can be set via constructor."""
        settings = LocaleDetectionSettings(query_param=False, accept_language=False)
        assert settings.query_param is False
        assert settings.url_prefix is True
        assert settings.user_session is True
        assert settings.cookie is True
        assert settings.accept_language is False


class TestCoreConfigurationLocaleDetection:
    """Test locale_detection field in CoreConfiguration."""

    def test_locale_detection_default(self):
        """Test that locale_detection has default settings."""
        config = CoreConfiguration(project=ProjectConfiguration())
        assert config.locale_detection is not None
        assert isinstance(config.locale_detection, LocaleDetectionSettings)
        assert config.locale_detection.accept_language is True

    def test_locale_detection_from_env_vars(self):
        """Test that locale_detection picks up LOCALE_* env vars."""
        with patch.dict("os.environ", {"LOCALE_ACCEPT_LANGUAGE": "false"}, clear=False):
            config = CoreConfiguration(project=ProjectConfiguration())
            assert config.locale_detection.accept_language is False
