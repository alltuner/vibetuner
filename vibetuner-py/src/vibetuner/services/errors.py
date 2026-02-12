# ABOUTME: Centralized, actionable error messages for unconfigured services.
# ABOUTME: Provides rich console output with example values, setup commands, and doc links.

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

_console = Console(stderr=True)

DOCS_BASE = "https://vibetuner.alltuner.com/docs"


def _build_message(
    *,
    service: str,
    env_vars: list[str],
    example_env: str,
    local_dev: str | None = None,
    disable_hint: str | None = None,
    docs_path: str = "configuration",
) -> str:
    """Build a multi-line error string with actionable fix instructions."""
    lines = [f"{service} is not configured.\n"]

    lines.append("Add the following to your .env file:\n")
    for line in example_env.strip().splitlines():
        lines.append(f"  {line}")
    lines.append("")

    if local_dev:
        lines.append("For local development:")
        for line in local_dev.strip().splitlines():
            lines.append(f"  {line}")
        lines.append("")

    if disable_hint:
        lines.append(f"To disable: {disable_hint}")
        lines.append("")

    lines.append(f"Docs: {DOCS_BASE}/{docs_path}")

    return "\n".join(lines)


def _print_rich_error(message: str, title: str) -> None:
    """Print error as a rich panel to stderr."""
    text = Text(message)
    _console.print(Panel(text, title=f"[red]{title}[/red]", border_style="red"))


# ── MongoDB ──────────────────────────────────────────────────────────

MONGODB_ERROR = _build_message(
    service="MongoDB",
    env_vars=["MONGODB_URL"],
    example_env="MONGODB_URL=mongodb://localhost:27017/mydb",
    local_dev="docker run -d -p 27017:27017 mongo:8",
    docs_path="configuration#mongodb",
)


def mongodb_not_configured() -> str:
    """Return (and optionally print) the MongoDB configuration error."""
    _print_rich_error(MONGODB_ERROR, "MongoDB not configured")
    return MONGODB_ERROR


# ── Redis ────────────────────────────────────────────────────────────

REDIS_ERROR = _build_message(
    service="Redis",
    env_vars=["REDIS_URL"],
    example_env="REDIS_URL=redis://localhost:6379/0",
    local_dev="docker run -d -p 6379:6379 redis:8-alpine",
    disable_hint="Remove background tasks from your tune.py or don't call get_worker().",
    docs_path="configuration#redis",
)


def redis_not_configured() -> str:
    """Return (and optionally print) the Redis configuration error."""
    _print_rich_error(REDIS_ERROR, "Redis not configured")
    return REDIS_ERROR


# ── S3 / R2 ─────────────────────────────────────────────────────────

S3_ERROR = _build_message(
    service="S3/R2 blob storage",
    env_vars=[
        "R2_BUCKET_ENDPOINT_URL",
        "R2_ACCESS_KEY",
        "R2_SECRET_KEY",
        "R2_DEFAULT_BUCKET_NAME",
    ],
    example_env=(
        "R2_BUCKET_ENDPOINT_URL=https://<account>.r2.cloudflarestorage.com\n"
        "R2_ACCESS_KEY=your-access-key\n"
        "R2_SECRET_KEY=your-secret-key\n"
        "R2_DEFAULT_BUCKET_NAME=my-bucket"
    ),
    local_dev=(
        "docker run -d -p 9000:9000 -p 9001:9001 \\\n"
        "  -e MINIO_ROOT_USER=minioadmin \\\n"
        "  -e MINIO_ROOT_PASSWORD=minioadmin \\\n"
        "  minio/minio server /data --console-address ':9001'"
    ),
    disable_hint="Don't import BlobService or get_blob_service if blob storage isn't needed.",
    docs_path="configuration#s3-r2",
)


def s3_not_configured() -> str:
    """Return (and optionally print) the S3/R2 configuration error."""
    _print_rich_error(S3_ERROR, "S3/R2 storage not configured")
    return S3_ERROR


# ── Email (Mailjet) ─────────────────────────────────────────────────

EMAIL_ERROR = _build_message(
    service="Email (Mailjet)",
    env_vars=["MAILJET_API_KEY", "MAILJET_API_SECRET"],
    example_env=("MAILJET_API_KEY=your-api-key\nMAILJET_API_SECRET=your-api-secret"),
    disable_hint="Don't import EmailService or get_email_service if email isn't needed.",
    docs_path="configuration#email",
)


def email_not_configured() -> str:
    """Return (and optionally print) the email configuration error."""
    _print_rich_error(EMAIL_ERROR, "Email service not configured")
    return EMAIL_ERROR
