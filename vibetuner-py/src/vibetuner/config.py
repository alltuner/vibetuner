import base64
import hashlib
import os
from datetime import datetime
from functools import cached_property
from typing import Annotated, Any, Literal, Self

import yaml
from pydantic import (
    UUID4,
    AnyUrl,
    Field,
    HttpUrl,
    MariaDBDsn,
    MongoDsn,
    MySQLDsn,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    UrlConstraints,
    computed_field,
    model_validator,
)
from pydantic_extra_types.color import Color as _PydanticColor
from pydantic_extra_types.language_code import LanguageAlpha2
from pydantic_settings import BaseSettings, SettingsConfigDict

from vibetuner.logging import logger

from .paths import PathSettings, config_vars as config_vars_path


class HexColor(_PydanticColor):
    """Subtype of :class:`pydantic_extra_types.color.Color` that always
    renders as long-form ``#rrggbb`` hex.

    Pydantic ``Color`` accepts named colors, ``rgb()``, ``hsl()``, hex
    shorthand etc., which is great for input flexibility. But its default
    ``__str__`` returns the named form when one matches (e.g.
    ``str(Color("#ffffff")) == "white"``), which is awkward when the value
    is interpolated into HTML attributes via Jinja's ``{{ color }}``.

    ``HexColor`` keeps all of ``Color``'s parsing (so ``"red"``,
    ``"rgb(255,0,0)"`` and ``"#f00"`` all work as input) but pins
    ``str(self)`` to ``#rrggbb`` so templates render predictably.
    """

    def __str__(self) -> str:  # type: ignore[override]
        return self.as_hex(format="long")


def _resolve_env_files() -> tuple[str, ...]:
    """Resolve .env file paths relative to the project root.

    Walks up from CWD to find the project root (like git finds .git/),
    then returns absolute paths to .env and .env.local there.
    Falls back to relative paths if no project root is found.
    """
    root = PathSettings._find_project_root()
    if root is None:
        return (".env", ".env.local")
    return (str(root / ".env"), str(root / ".env.local"))


_ENV_FILES = _resolve_env_files()


class SQLiteDsn(AnyUrl):
    """A type that will accept any SQLite DSN.

    * User info not required
    * TLD not required
    * Host not required (file-based database)
    """

    _constraints = UrlConstraints(
        allowed_schemes=[
            "sqlite",
            "sqlite+aiosqlite",
            "sqlite+pysqlite",
        ],
        host_required=False,
    )


current_year: int = datetime.now().year

UnprivilegedPort = Annotated[int, Field(ge=1024, le=65535)]

# Placeholder session key the config field defaults to and the template's .env
# ships. The startup validator refuses to run with a known placeholder in
# production so a project can never sign prod sessions with a publicly-known key.
DEFAULT_SESSION_KEY_PLACEHOLDER = "CHANGE_ME_RUN_vibetuner_crypto_generate"

# Every session key value that is publicly known and therefore unsafe to sign
# sessions with. Includes the historical placeholder so projects upgrading from
# an older scaffold (whose .env still carries it) are guarded on upgrade.
KNOWN_INSECURE_SESSION_KEYS = frozenset(
    {"ct-!secret-must-change-me", DEFAULT_SESSION_KEY_PLACEHOLDER}
)


class SecurityHeadersSettings(BaseSettings):
    """Settings for built-in security headers middleware.

    All CSP extra_* fields accept space-separated source expressions that are
    appended to the corresponding CSP directive.
    """

    enabled: bool = True
    extra_script_src: str = ""
    extra_style_src: str = ""
    extra_font_src: str = ""
    extra_connect_src: str = ""
    extra_img_src: str = ""
    extra_media_src: str = ""
    frame_ancestors: str = "'self'"
    enforce_csp_in_debug: bool = True
    style_src_strict: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_prefix="CSP_",
        env_file=_ENV_FILES,
    )


class RateLimitSettings(BaseSettings):
    """Settings for rate limiting middleware.

    Rate limit strings follow the format: "X per Y" or "X/Y"
    where X is the number and Y is the period (second, minute, hour, day).
    Examples: "10/minute", "100/hour", "5 per second"
    """

    enabled: bool = True
    default_limits: list[str] = []
    # Per-IP limit applied to unauthenticated auth endpoints (magic-link send,
    # OAuth initiation) to curb email flooding and account enumeration.
    auth_limits: str = "5/minute"
    headers_enabled: bool = True
    strategy: str = "fixed-window"
    swallow_errors: bool = True

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_prefix="RATE_LIMIT_",
        env_file=_ENV_FILES,
    )


class LocaleDetectionSettings(BaseSettings):
    """Settings for locale detection selectors.

    All selectors are enabled by default. The order is fixed:
    1. query_param - ?l=ca query parameter
    2. url_prefix - /ca/... path prefix
    3. user_session - authenticated user's stored preference
    4. cookie - language cookie
    5. accept_language - browser Accept-Language header
    """

    query_param: bool = True
    url_prefix: bool = True
    user_session: bool = True
    cookie: bool = True
    accept_language: bool = True

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_prefix="LOCALE_",
        env_file=_ENV_FILES,
    )


class BrandSettings(BaseSettings):
    """App-level brand colors for surfaces CSS variables can't reach.

    Read from ``BRAND_*`` env vars. These cover three places where
    DaisyUI/CSS-variable theming doesn't apply:

    - ``<link rel="mask-icon" color>`` (Safari pinned tab) and
      ``<meta msapplication-TileColor>`` (Windows tile) — both driven by
      :attr:`primary_color`.
    - ``<meta theme-color>`` (browser chrome / Android status bar) and the
      PWA webmanifest's ``theme_color`` / ``background_color`` — driven by
      :attr:`browser_theme_color`.
    - Inline button color in HTML emails (e.g. magic-link CTA) — driven by
      :attr:`email_button_color`, which falls back to :attr:`primary_color`.

    For per-tenant theming of in-page colors, use
    :class:`vibetuner.models.TenantTheme` instead. ``BrandSettings`` is
    deliberately app-level: favicon meta is set before CSS runs, and the
    email-sending code path doesn't currently see per-request context.
    """

    primary_color: HexColor = HexColor("#5b2333")
    browser_theme_color: HexColor = HexColor("#ffffff")
    email_button_color: HexColor | None = None  # falls back to primary_color

    @property
    def email_button(self) -> HexColor:
        """The color used for HTML-email CTA buttons.

        Falls back to :attr:`primary_color` when ``BRAND_EMAIL_BUTTON_COLOR``
        is not set, so a single ``BRAND_PRIMARY_COLOR`` covers both surfaces
        in the common case.
        """
        return self.email_button_color or self.primary_color

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_prefix="BRAND_",
        env_file=_ENV_FILES,
    )


class MailSettings(BaseSettings):
    """Mail provider configuration. Read from MAIL_* env vars."""

    provider: Literal["resend", "mailjet", "cloudflare"] | None = None

    # Resend
    resend_api_key: SecretStr | None = None

    # Mailjet
    mailjet_api_key: SecretStr | None = None
    mailjet_api_secret: SecretStr | None = None

    # Cloudflare Email Service
    cloudflare_api_token: SecretStr | None = None
    cloudflare_account_id: str | None = None

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_prefix="MAIL_",
        env_file=_ENV_FILES,
    )


def _load_project_config() -> "ProjectConfiguration":
    if config_vars_path is None or not config_vars_path.exists():
        return ProjectConfiguration()

    yaml_data = yaml.safe_load(config_vars_path.read_text(encoding="utf-8"))
    return ProjectConfiguration(**yaml_data)


class ProjectConfiguration(BaseSettings):
    @classmethod
    def from_project_config(cls) -> "ProjectConfiguration":
        return _load_project_config()

    project_slug: str = "default_project"
    project_name: str = "default_project"

    project_description: str = "A default project description."

    # Language Related Settings
    supported_languages: set[LanguageAlpha2] | None = None
    default_language: LanguageAlpha2 = LanguageAlpha2("en")

    # AWS Parameters
    aws_default_region: str = "eu-central-1"

    # Company Name
    company_name: str = "Acme Corp"

    # From Email for transactional emails
    from_email: str = "no-reply@example.com"

    # Copyright
    copyright_start: Annotated[int, Field(strict=True, gt=1714, lt=2048)] = current_year

    # Analytics
    umami_website_id: UUID4 | None = None

    # Fully Qualified Domain Name
    fqdn: str | None = None

    @cached_property
    def languages(self) -> set[str]:
        if self.supported_languages is None:
            return {self.language}

        return {
            str(lang) for lang in (*self.supported_languages, self.default_language)
        }

    @cached_property
    def language(self) -> str:
        return str(self.default_language)

    @cached_property
    def copyright(self) -> str:
        year_part = (
            f"{self.copyright_start}-{current_year}"
            if self.copyright_start and self.copyright_start != current_year
            else str(current_year)
        )
        return f"© {year_part}{f' {self.company_name}' if self.company_name else ''}"

    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_file=_ENV_FILES
    )


class CoreConfiguration(BaseSettings):
    project: ProjectConfiguration = ProjectConfiguration.from_project_config()

    debug: bool = False
    environment: Literal["dev", "prod"] = "dev"
    session_key: SecretStr = SecretStr(DEFAULT_SESSION_KEY_PLACEHOLDER)

    # Database and Cache URLs
    mongodb_url: MongoDsn | None = None
    redis_url: RedisDsn | None = None
    database_url: PostgresDsn | MariaDBDsn | MySQLDsn | SQLiteDsn | None = None

    # Optional test-only MongoDB DSN. When set, the pytest fixtures target this
    # server instead of ``mongodb_url`` so a project whose ``.env`` points at a
    # remote/production cluster can still run its suite against a local Mongo.
    test_mongodb_url: MongoDsn | None = None

    # Optional test-only Redis DSN. When set, the pytest fixtures target this
    # server instead of ``redis_url`` so a project whose ``.env`` points at a
    # remote/production Redis can still run its suite against a local Redis.
    test_redis_url: RedisDsn | None = None

    # Mail provider settings (MAIL_* env vars)
    mail: MailSettings = Field(default_factory=MailSettings)

    # App-level brand colors (BRAND_* env vars). Used in places CSS variables
    # can't reach: favicon meta, webmanifest theme/background, email buttons.
    brand: BrandSettings = Field(default_factory=BrandSettings)

    r2_default_bucket_name: str | None = None
    r2_bucket_endpoint_url: HttpUrl | None = None
    r2_access_key: SecretStr | None = None
    r2_secret_key: SecretStr | None = None
    r2_default_region: str = "auto"

    # OAuth provider credentials (read from env / .env)
    google_client_id: SecretStr | None = None
    google_client_secret: SecretStr | None = None
    github_client_id: SecretStr | None = None
    github_client_secret: SecretStr | None = None

    # Passphrase for Fernet-encrypting fields at rest in MongoDB.
    # Any Beanie document field typed as ``EncryptedStr`` (via EncryptedFieldsMixin)
    # is transparently encrypted on save and decrypted on load when this key is set.
    field_encryption_key: str | None = None

    worker_concurrency: int = 16

    # How long (seconds) streaq waits for new tasks before re-checking idle tasks.
    # Matches streaq's Worker(idle_timeout=...) default so the two stay in sync.
    # Must be set here so worker_redis_kwargs can derive safe coredis timeouts.
    worker_idle_timeout: float = 60.0

    # Redis connection resilience for long-lived clients (e.g. the streaq worker).
    # Without a socket timeout, a silently-dropped TCP connection leaves a blocking
    # read that never returns, wedging the worker's event loop indefinitely. A
    # non-zero socket_timeout turns that hang into a raised error so the worker
    # reconnects or exits and is restarted. Set the timeouts to 0 to disable.
    redis_socket_timeout: float = 30.0
    redis_socket_connect_timeout: float = 10.0
    redis_socket_keepalive: bool = True
    redis_health_check_interval: float = 30.0

    # Liveness watchdog: a thread force-exits the worker if the event loop
    # stops ticking for longer than the timeout, so a stalled (but not crashed)
    # process is restarted by its `restart` policy. Set the timeout to 0 to
    # disable. The interval is how often the loop beats and the thread checks.
    worker_watchdog_timeout: float = 60.0
    worker_watchdog_interval: float = 5.0

    # Port configuration (read from DEV_PORT / WORKER_PORT env or .env.local)
    dev_port: UnprivilegedPort | None = None
    worker_port: UnprivilegedPort | None = None

    @staticmethod
    def _compute_auto_port(path: str | None = None) -> int:
        """Deterministic port from directory path. Range: 10000-13999."""
        target_path = path or os.getcwd()
        hash_bytes = hashlib.sha256(target_path.encode()).digest()
        hash_int = int.from_bytes(hash_bytes[:4], "big")
        return 10000 + (hash_int % 4000)

    @computed_field
    @cached_property
    def resolved_port(self) -> int:
        """Frontend port: DEV_PORT if set, auto-calculated in dev, 8000 in prod."""
        if self.dev_port is not None:
            return self.dev_port
        if self.environment == "prod":
            return 8000
        return self._compute_auto_port()

    @computed_field
    @cached_property
    def resolved_worker_port(self) -> int:
        """Worker port: WORKER_PORT if set, otherwise 10000 + resolved_port."""
        if self.worker_port is not None:
            return self.worker_port
        return 10000 + self.resolved_port

    @computed_field
    @cached_property
    def version(self) -> str:
        """Project version computed lazily from git or package metadata."""
        from vibetuner.versioning import get_version

        return get_version()

    # Rate limiting settings
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)

    # Locale detection settings
    locale_detection: LocaleDetectionSettings = Field(
        default_factory=LocaleDetectionSettings
    )

    # Security headers settings
    security_headers: SecurityHeadersSettings = Field(
        default_factory=SecurityHeadersSettings
    )

    # Proxy configuration for X-Forwarded-For/Proto headers
    # Comma-separated list of trusted proxy IPs/CIDRs (e.g., "127.0.0.1,192.168.1.0/24")
    # SECURITY: Only IPs in this list can set forwarded headers. Use "*" to trust all (NOT recommended for production)
    trusted_proxy_hosts: str = "127.0.0.1"

    # OAuth relay URL for shared redirect URI across multiple local apps.
    # When set, OAuth flows use this stable URL instead of the app's own URL.
    # Example: "https://oauth.localdev.alltuner.com:28000"
    oauth_relay_url: HttpUrl | None = None

    @cached_property
    def trusted_proxy_hosts_list(self) -> list[str]:
        """Parse trusted proxy hosts into a list for Granian's proxy header wrapper."""
        return [h.strip() for h in self.trusted_proxy_hosts.split(",") if h.strip()]

    @computed_field
    @cached_property
    def v_hash(self) -> str:
        hash_object = hashlib.sha256(self.version.encode("utf-8"))
        hash_bytes = hash_object.digest()

        b64_hash = base64.urlsafe_b64encode(hash_bytes).decode("utf-8")

        url_safe_hash = b64_hash.rstrip("=")[:8]

        return url_safe_hash

    @property
    def workers_available(self) -> bool:
        return self.redis_url is not None

    @property
    def worker_redis_kwargs(self) -> dict[str, Any]:
        """Connection-resilience kwargs for the streaq worker's coredis client.

        Streaq builds its Redis client with coredis, so these use coredis
        kwarg names. ``stream_timeout`` turns a silently-dropped connection's
        blocking read into a raised error instead of an indefinite hang, and
        ``max_idle_time`` recycles long-idle connections so a stale one is
        never reused. A timeout of 0 is omitted, which coredis treats as no
        timeout.

        Both ``stream_timeout`` and ``max_idle_time`` must safely exceed
        ``worker_idle_timeout``: streaq calls ``XREADGROUP BLOCK idle_timeout``
        on the Redis server, and coredis would otherwise time out during that
        legitimate blocking wait and raise a premature timeout error.
        """
        kwargs: dict[str, Any] = {
            "socket_keepalive": self.redis_socket_keepalive,
        }
        safe_timeout = max(
            self.redis_socket_timeout, self.worker_idle_timeout * 1.5
        )
        if self.redis_socket_timeout > 0:
            kwargs["stream_timeout"] = safe_timeout
        if self.redis_socket_connect_timeout > 0:
            kwargs["connect_timeout"] = self.redis_socket_connect_timeout
        if self.redis_health_check_interval > 0:
            safe_idle = max(self.redis_health_check_interval, self.worker_idle_timeout * 1.5)
            kwargs["max_idle_time"] = int(safe_idle)
        return kwargs

    @property
    def _redis_resilience_kwargs(self) -> dict[str, Any]:
        """Shared resilience kwargs for redis-py clients (``redis.asyncio``).

        ``socket_keepalive`` and a periodic ``health_check_interval`` PING let a
        silently-dropped TCP connection be detected and recycled. A timeout of 0
        omits the corresponding kwarg.
        """
        kwargs: dict[str, Any] = {
            "socket_keepalive": self.redis_socket_keepalive,
        }
        if self.redis_socket_connect_timeout > 0:
            kwargs["socket_connect_timeout"] = self.redis_socket_connect_timeout
        if self.redis_health_check_interval > 0:
            kwargs["health_check_interval"] = int(self.redis_health_check_interval)
        return kwargs

    @property
    def redis_client_kwargs(self) -> dict[str, Any]:
        """redis-py kwargs for command clients (cache, health, SSE publish).

        These run only non-blocking commands, so a ``socket_timeout`` safely turns
        a silently-dropped connection's blocking read into a raised error instead
        of an indefinite hang. A timeout of 0 omits it.
        """
        kwargs = self._redis_resilience_kwargs
        if self.redis_socket_timeout > 0:
            kwargs["socket_timeout"] = self.redis_socket_timeout
        return kwargs

    @property
    def redis_subscriber_kwargs(self) -> dict[str, Any]:
        """redis-py kwargs for the SSE pub/sub subscriber connection.

        A subscriber blocks indefinitely waiting for the next message, so it must
        never carry a ``socket_timeout`` — that would raise ``TimeoutError`` on any
        channel idle longer than the timeout and kill the listener. Liveness relies
        on ``health_check_interval`` PINGs and TCP keepalive instead.
        """
        kwargs = self._redis_resilience_kwargs
        kwargs["socket_timeout"] = None
        return kwargs

    @property
    def resolved_test_mongodb_url(self) -> MongoDsn | None:
        """MongoDB server the test fixtures target.

        Prefers ``test_mongodb_url`` (``TEST_MONGODB_URL``) when set so a
        prod-pointing ``mongodb_url`` stays out of the test path, falling back
        to ``mongodb_url`` otherwise.
        """
        return self.test_mongodb_url or self.mongodb_url

    @property
    def resolved_test_redis_url(self) -> RedisDsn | None:
        """Redis server the test fixtures target.

        Prefers ``test_redis_url`` (``TEST_REDIS_URL``) when set so a
        prod-pointing ``redis_url`` stays out of the test path, falling back
        to ``redis_url`` otherwise.
        """
        return self.test_redis_url or self.redis_url

    @cached_property
    def mongo_dbname(self) -> str:
        return self.project.project_slug

    @cached_property
    def redis_key_prefix(self) -> str:
        """Returns the Redis key prefix for namespacing all Redis keys by project and environment.

        Format: "{project_slug}:{env}:" for dev, "{project_slug}:" for prod.
        """
        if self.environment == "dev":
            return f"{self.project.project_slug}:dev:"
        return f"{self.project.project_slug}:"

    @model_validator(mode="after")
    def fail_closed_on_placeholder_session_key(self) -> Self:
        """Refuse to run in production with a known placeholder session key.

        Sessions are signed with ``session_key``; any publicly-known
        placeholder (the shipped default or a historical one left in an
        upgraded project's ``.env``) would let anyone forge a session, so a
        production startup (``environment == "prod"``) fails fast. Outside
        production it only warns, keeping local development friction free while
        making the required action obvious before deploy.
        """
        if self.session_key.get_secret_value() not in KNOWN_INSECURE_SESSION_KEYS:
            return self

        if self.environment == "prod":
            raise ValueError(
                "SESSION_KEY is still the placeholder value. Set a unique "
                "SESSION_KEY in your .env before running in production. "
                "Generate one with: vibetuner crypto generate-key"
            )

        logger.warning(
            "SESSION_KEY is the insecure placeholder value. This is only "
            "tolerated outside production. Set a unique SESSION_KEY in your "
            ".env (generate one with: vibetuner crypto generate-key) before "
            "deploying."
        )
        return self

    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_file=_ENV_FILES
    )


settings = CoreConfiguration()


logger.info("Configuration loaded for project: {}", settings.project.project_name)
