# ABOUTME: Unit tests for vibetuner.config module
# ABOUTME: Tests environment configuration, locale detection, and redis_key_prefix computation
# ruff: noqa: S101

from unittest.mock import patch

import pytest
from vibetuner.config import (
    _ENV_FILES,
    CoreConfiguration,
    LocaleDetectionSettings,
    ProjectConfiguration,
)


class TestProjectConfigurationEnvFile:
    """Test that ProjectConfiguration loads deploy-config from .env files.

    Deploy-time fields like from_email have no stable home in the copier
    questionnaire (non-template keys are stripped on copier update), so they
    must be settable via .env like the other settings classes (#1970).
    """

    def test_declares_env_file(self):
        """ProjectConfiguration wires .env loading, matching the sibling
        settings classes (CoreConfiguration, MailSettings, BrandSettings, ...)."""
        assert ProjectConfiguration.model_config.get("env_file") == _ENV_FILES

    def test_from_email_loads_from_dotenv(self, tmp_path):
        """from_email is populated from a .env file at the project root."""
        env_file = tmp_path / ".env"
        env_file.write_text("FROM_EMAIL=ops@example.com\n")
        with patch.dict("os.environ", {}, clear=True):
            project = ProjectConfiguration(_env_file=str(env_file))
            assert project.from_email == "ops@example.com"

    def test_from_email_falls_back_to_default(self):
        """Without .env or env var, from_email keeps its default."""
        with patch.dict("os.environ", {}, clear=True):
            project = ProjectConfiguration(_env_file=None)
            assert project.from_email == "no-reply@example.com"


class TestCoreConfigurationEnvironment:
    """Test environment configuration in CoreConfiguration."""

    def test_environment_default_is_dev(self):
        """Test that environment defaults to 'dev'."""
        with patch.dict("os.environ", {}, clear=True):
            config = CoreConfiguration(project=ProjectConfiguration())
            assert config.environment == "dev"

    def test_environment_from_env_var(self):
        """Test that environment can be set via ENVIRONMENT env var."""
        with patch.dict(
            "os.environ",
            {"ENVIRONMENT": "prod", "SESSION_KEY": "real-session-key"},
            clear=False,
        ):
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
        config = CoreConfiguration(
            project=project, environment="prod", session_key="real-session-key"
        )
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
            config = CoreConfiguration(
                project=project, environment=env, session_key="real-session-key"
            )
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


class TestResolvedTestMongodbUrl:
    """Test resolved_test_mongodb_url fallback for the test fixtures."""

    def test_falls_back_to_mongodb_url_when_test_url_unset(self):
        """Without TEST_MONGODB_URL, tests target the production mongodb_url."""
        config = CoreConfiguration(
            project=ProjectConfiguration(),
            mongodb_url="mongodb://prod-host:27017/",
        )
        assert str(config.resolved_test_mongodb_url) == "mongodb://prod-host:27017/"

    def test_prefers_test_url_when_set(self):
        """TEST_MONGODB_URL wins over mongodb_url so a prod .env stays isolated."""
        config = CoreConfiguration(
            project=ProjectConfiguration(),
            mongodb_url="mongodb://prod-host:27017/",
            test_mongodb_url="mongodb://localhost:27018/",
        )
        assert str(config.resolved_test_mongodb_url) == "mongodb://localhost:27018/"

    def test_is_none_when_neither_set(self):
        """Resolves to None when no Mongo URL is configured at all."""
        config = CoreConfiguration(project=ProjectConfiguration())
        assert config.resolved_test_mongodb_url is None

    def test_test_url_from_env_var(self):
        """test_mongodb_url is read from the TEST_MONGODB_URL env var."""
        with patch.dict(
            "os.environ", {"TEST_MONGODB_URL": "mongodb://localhost:27018/"}
        ):
            config = CoreConfiguration(project=ProjectConfiguration())
            assert str(config.resolved_test_mongodb_url) == "mongodb://localhost:27018/"


class TestResolvedTestRedisUrl:
    """Test resolved_test_redis_url fallback for the test fixtures."""

    def test_falls_back_to_redis_url_when_test_url_unset(self):
        """Without TEST_REDIS_URL, tests target the production redis_url."""
        config = CoreConfiguration(
            project=ProjectConfiguration(),
            redis_url="redis://prod-host:6379/0",
        )
        assert str(config.resolved_test_redis_url) == "redis://prod-host:6379/0"

    def test_prefers_test_url_when_set(self):
        """TEST_REDIS_URL wins over redis_url so a prod .env stays isolated."""
        config = CoreConfiguration(
            project=ProjectConfiguration(),
            redis_url="redis://prod-host:6379/0",
            test_redis_url="redis://localhost:6380/0",
        )
        assert str(config.resolved_test_redis_url) == "redis://localhost:6380/0"

    def test_is_none_when_neither_set(self):
        """Resolves to None when no Redis URL is configured at all."""
        config = CoreConfiguration(project=ProjectConfiguration())
        assert config.resolved_test_redis_url is None

    def test_test_url_from_env_var(self):
        """test_redis_url is read from the TEST_REDIS_URL env var."""
        with patch.dict("os.environ", {"TEST_REDIS_URL": "redis://localhost:6380/0"}):
            config = CoreConfiguration(project=ProjectConfiguration())
            assert str(config.resolved_test_redis_url) == "redis://localhost:6380/0"


class TestLoadProjectConfig:
    """Test _load_project_config behavior outside a project directory."""

    def test_returns_defaults_when_no_project_root(self):
        """Config loading returns defaults when config_vars_path is None."""
        with patch("vibetuner.config.config_vars_path", None):
            from vibetuner.config import _load_project_config

            result = _load_project_config()
            assert isinstance(result, ProjectConfiguration)
            assert result.project_slug == "default_project"


class TestWorkerRedisKwargs:
    """Test worker_redis_kwargs resilience options for the streaq coredis client."""

    def test_defaults_enable_resilience(self):
        """By default, stream/connect timeouts, keepalive and idle recycling are on."""
        config = CoreConfiguration(project=ProjectConfiguration())
        kwargs = config.worker_redis_kwargs
        assert kwargs["stream_timeout"] == 30.0
        assert kwargs["connect_timeout"] == 10.0
        assert kwargs["socket_keepalive"] is True
        assert kwargs["max_idle_time"] == 30

    def test_kwargs_accepted_by_coredis_connection(self):
        """The kwargs must construct a coredis connection without raising.

        Regression for the 10.19.0 startup crash: redis-py kwarg names
        (health_check_interval, socket_timeout) reached streaq's coredis client
        and coredis rejected them with a TypeError during lifespan startup.
        """
        from coredis.connection import TCPConnection, TCPLocation

        config = CoreConfiguration(project=ProjectConfiguration())
        location = TCPLocation(host="localhost", port=6379)
        # Constructs the connection object (does not open a socket).
        TCPConnection(location, **config.worker_redis_kwargs)

    def test_stream_timeout_disabled_when_zero(self):
        """A zero socket_timeout is omitted so coredis treats it as no timeout."""
        config = CoreConfiguration(
            project=ProjectConfiguration(), redis_socket_timeout=0
        )
        assert "stream_timeout" not in config.worker_redis_kwargs

    def test_connect_timeout_disabled_when_zero(self):
        """A zero socket_connect_timeout is omitted."""
        config = CoreConfiguration(
            project=ProjectConfiguration(), redis_socket_connect_timeout=0
        )
        assert "connect_timeout" not in config.worker_redis_kwargs

    def test_idle_recycling_disabled_when_zero(self):
        """A zero health_check_interval omits max_idle_time."""
        config = CoreConfiguration(
            project=ProjectConfiguration(), redis_health_check_interval=0
        )
        assert "max_idle_time" not in config.worker_redis_kwargs

    def test_overrides_from_env_vars(self):
        """REDIS_SOCKET_* and REDIS_HEALTH_CHECK_INTERVAL env vars are honored."""
        with patch.dict(
            "os.environ",
            {
                "REDIS_SOCKET_TIMEOUT": "5",
                "REDIS_SOCKET_CONNECT_TIMEOUT": "2",
                "REDIS_SOCKET_KEEPALIVE": "false",
                "REDIS_HEALTH_CHECK_INTERVAL": "15",
            },
            clear=False,
        ):
            config = CoreConfiguration(project=ProjectConfiguration())
            kwargs = config.worker_redis_kwargs
            assert kwargs["stream_timeout"] == 5.0
            assert kwargs["connect_timeout"] == 2.0
            assert kwargs["socket_keepalive"] is False
            assert kwargs["max_idle_time"] == 15


class TestRedisClientKwargs:
    """Test redis-py kwargs for the shared async clients (redis.asyncio)."""

    def test_command_client_carries_read_timeout(self):
        """Command clients (cache, health, SSE publish) get a socket read timeout.

        They run only non-blocking commands, so a read timeout safely turns a
        silently-dropped connection's blocking read into a raised error.
        """
        config = CoreConfiguration(project=ProjectConfiguration())
        kwargs = config.redis_client_kwargs
        assert kwargs["socket_timeout"] == 30.0
        assert kwargs["socket_connect_timeout"] == 10.0
        assert kwargs["socket_keepalive"] is True
        assert kwargs["health_check_interval"] == 30

    def test_subscriber_never_carries_read_timeout(self):
        """The SSE pub/sub subscriber must never carry a socket read timeout.

        A subscriber blocks indefinitely between messages; a read timeout would
        raise on any idle channel and kill the listener (issue #1958). Liveness
        relies on health_check_interval PINGs and TCP keepalive instead.
        """
        config = CoreConfiguration(project=ProjectConfiguration())
        kwargs = config.redis_subscriber_kwargs
        assert kwargs["socket_timeout"] is None
        assert kwargs["socket_connect_timeout"] == 10.0
        assert kwargs["socket_keepalive"] is True
        assert kwargs["health_check_interval"] == 30

    def test_subscriber_drops_timeout_even_when_configured(self):
        """A non-zero redis_socket_timeout still leaves the subscriber timeout-free."""
        config = CoreConfiguration(
            project=ProjectConfiguration(), redis_socket_timeout=5
        )
        assert config.redis_subscriber_kwargs["socket_timeout"] is None

    def test_command_kwargs_accepted_by_redis_connection(self):
        """The kwargs must construct a redis-py async client without raising."""
        import redis.asyncio as aioredis

        config = CoreConfiguration(project=ProjectConfiguration())
        client = aioredis.Redis(**config.redis_client_kwargs)
        assert client is not None

    def test_command_timeout_disabled_when_zero(self):
        """A zero socket_timeout is omitted from command kwargs."""
        config = CoreConfiguration(
            project=ProjectConfiguration(), redis_socket_timeout=0
        )
        assert "socket_timeout" not in config.redis_client_kwargs

    def test_health_check_disabled_when_zero(self):
        """A zero health_check_interval omits health_check_interval from both."""
        config = CoreConfiguration(
            project=ProjectConfiguration(), redis_health_check_interval=0
        )
        assert "health_check_interval" not in config.redis_client_kwargs
        assert "health_check_interval" not in config.redis_subscriber_kwargs


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
