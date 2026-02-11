# ABOUTME: Validates project setup: structure, env vars, service connectivity, models, templates.
# ABOUTME: Provides `vibetuner doctor` CLI command for diagnosing project issues.

import importlib.metadata
import socket
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import typer
from rich.console import Console
from rich.table import Table

from vibetuner.logging import logger

doctor_app = typer.Typer(help="Validate project setup", invoke_without_command=True)
console = Console()


CheckStatus = Literal["ok", "warn", "error", "skip"]

_STATUS_ICONS: dict[CheckStatus, str] = {
    "ok": "[green]\u2713[/green]",
    "warn": "[yellow]![/yellow]",
    "error": "[red]\u2717[/red]",
    "skip": "[dim]-[/dim]",
}


class CheckResult:
    __slots__ = ("name", "status", "message")

    def __init__(self, name: str, status: CheckStatus, message: str) -> None:
        self.name = name
        self.status = status
        self.message = message


def _check_project_structure(root: Path | None) -> list[CheckResult]:
    results: list[CheckResult] = []

    if root is None:
        results.append(
            CheckResult(
                "Project root",
                "error",
                "Not in a vibetuner project directory",
            )
        )
        return results

    results.append(CheckResult("Project root", "ok", str(root)))

    copier_answers = root / ".copier-answers.yml"
    if copier_answers.exists():
        results.append(CheckResult(".copier-answers.yml", "ok", "Found"))
    else:
        results.append(
            CheckResult(
                ".copier-answers.yml", "error", "Missing — run vibetuner scaffold new"
            )
        )

    env_file = root / ".env"
    if env_file.exists():
        results.append(CheckResult(".env file", "ok", "Found"))
    else:
        results.append(
            CheckResult(".env file", "warn", "Missing — copy from .env.example")
        )

    src_dir = root / "src"
    if src_dir.is_dir():
        packages = [
            d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
        if packages:
            results.append(
                CheckResult("src/ layout", "ok", f"Package: {packages[0].name}")
            )
        else:
            results.append(
                CheckResult("src/ layout", "error", "No package found in src/")
            )
    else:
        results.append(CheckResult("src/ layout", "error", "src/ directory not found"))

    return results


def _check_tune_py(root: Path | None) -> list[CheckResult]:
    if root is None:
        return [CheckResult("tune.py", "skip", "No project root")]

    from vibetuner.pyproject import get_project_name

    package_name = get_project_name()
    if package_name is None:
        return [CheckResult("tune.py", "skip", "Cannot determine package name")]

    src_tune = root / "src" / package_name / "tune.py"
    if not src_tune.exists():
        return [CheckResult("tune.py", "warn", "Not found — zero-config mode active")]

    try:
        from vibetuner.loader import ConfigurationError, load_app_config

        load_app_config()
        return [CheckResult("tune.py", "ok", "Loaded successfully")]
    except ConfigurationError as exc:
        return [CheckResult("tune.py", "error", str(exc))]
    except Exception as exc:
        return [CheckResult("tune.py", "error", f"Import error: {exc}")]


def _check_env_vars() -> list[CheckResult]:
    results: list[CheckResult] = []
    try:
        from vibetuner.config import CoreConfiguration, ProjectConfiguration

        config = CoreConfiguration(project=ProjectConfiguration())
    except Exception as exc:
        return [CheckResult("Configuration", "error", f"Failed to load: {exc}")]

    results.append(
        CheckResult(
            "Environment",
            "ok",
            config.environment,
        )
    )

    if config.session_key.get_secret_value() == "ct-!secret-must-change-me":
        results.append(
            CheckResult(
                "SESSION_KEY", "warn", "Using default — set a unique secret in .env"
            )
        )
    else:
        results.append(CheckResult("SESSION_KEY", "ok", "Custom value set"))

    return results


def _can_connect(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _check_service_connectivity() -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        from vibetuner.config import CoreConfiguration, ProjectConfiguration

        config = CoreConfiguration(project=ProjectConfiguration())
    except Exception:
        return [CheckResult("Services", "skip", "Cannot load configuration")]

    # MongoDB
    if config.mongodb_url:
        parsed = urlparse(str(config.mongodb_url))
        host = parsed.hostname or "localhost"
        port = parsed.port or 27017
        if _can_connect(host, port):
            results.append(CheckResult("MongoDB", "ok", f"{host}:{port} reachable"))
        else:
            results.append(
                CheckResult("MongoDB", "error", f"{host}:{port} unreachable")
            )
    else:
        results.append(CheckResult("MongoDB", "warn", "MONGODB_URL not configured"))

    # Redis
    if config.redis_url:
        parsed = urlparse(str(config.redis_url))
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        if _can_connect(host, port):
            results.append(CheckResult("Redis", "ok", f"{host}:{port} reachable"))
        else:
            results.append(CheckResult("Redis", "error", f"{host}:{port} unreachable"))
    else:
        results.append(CheckResult("Redis", "skip", "REDIS_URL not configured"))

    # R2 / S3
    if config.r2_bucket_endpoint_url:
        parsed = urlparse(str(config.r2_bucket_endpoint_url))
        host = parsed.hostname or ""
        port = parsed.port or 443
        if _can_connect(host, port):
            results.append(CheckResult("R2/S3 endpoint", "ok", f"{host} reachable"))
        else:
            results.append(CheckResult("R2/S3 endpoint", "warn", f"{host} unreachable"))
    else:
        results.append(CheckResult("R2/S3 endpoint", "skip", "Not configured"))

    return results


def _check_models() -> list[CheckResult]:
    try:
        from vibetuner.mongo import get_all_models

        models = get_all_models()
        return [
            CheckResult(
                "Registered models",
                "ok",
                f"{len(models)} model(s): {', '.join(m.__name__ for m in models)}",
            )
        ]
    except Exception as exc:
        return [CheckResult("Registered models", "warn", f"Cannot load models: {exc}")]


def _check_templates(root: Path | None) -> list[CheckResult]:
    if root is None:
        return [CheckResult("Templates", "skip", "No project root")]

    results: list[CheckResult] = []
    templates_dir = root / "templates"

    if not templates_dir.is_dir():
        results.append(CheckResult("Templates dir", "warn", "templates/ not found"))
        return results

    results.append(CheckResult("Templates dir", "ok", "Found"))

    # Check for common Jinja2 syntax issues in template files
    template_files = list(templates_dir.rglob("*.html")) + list(
        templates_dir.rglob("*.j2")
    )
    bad_files: list[str] = []
    for tf in template_files:
        try:
            content = tf.read_text(encoding="utf-8")
            # Basic syntax check: unmatched block tags
            opens = content.count("{%")
            closes = content.count("%}")
            if opens != closes:
                bad_files.append(tf.relative_to(root).as_posix())
        except Exception:
            bad_files.append(tf.relative_to(root).as_posix())

    if bad_files:
        results.append(
            CheckResult(
                "Template syntax",
                "warn",
                f"Possible issues in: {', '.join(bad_files[:5])}",
            )
        )
    elif template_files:
        results.append(
            CheckResult(
                "Template syntax", "ok", f"{len(template_files)} file(s) checked"
            )
        )

    return results


def _check_dependencies() -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        vt_version = importlib.metadata.version("vibetuner")
        results.append(CheckResult("vibetuner", "ok", f"v{vt_version}"))
    except importlib.metadata.PackageNotFoundError:
        results.append(CheckResult("vibetuner", "error", "Package not installed"))

    key_packages = ["fastapi", "beanie", "granian", "pydantic"]
    for pkg in key_packages:
        try:
            ver = importlib.metadata.version(pkg)
            results.append(CheckResult(pkg, "ok", f"v{ver}"))
        except importlib.metadata.PackageNotFoundError:
            results.append(CheckResult(pkg, "warn", "Not installed"))

    return results


def _check_port_availability() -> list[CheckResult]:
    results: list[CheckResult] = []

    for port, label in [(8000, "Frontend (8000)"), (11111, "Worker UI (11111)")]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.bind(("127.0.0.1", port))
            results.append(CheckResult(label, "ok", "Available"))
        except OSError:
            results.append(CheckResult(label, "warn", "Port already in use"))

    return results


@doctor_app.callback(invoke_without_command=True)
def doctor() -> None:
    """Run diagnostic checks on your vibetuner project."""
    from vibetuner.paths import paths

    root = paths.root

    all_results: list[CheckResult] = []

    sections: list[tuple[str, list[CheckResult]]] = [
        ("Project Structure", _check_project_structure(root)),
        ("App Configuration", _check_tune_py(root)),
        ("Environment", _check_env_vars()),
        ("Service Connectivity", _check_service_connectivity()),
        ("Models", _check_models()),
        ("Templates", _check_templates(root)),
        ("Dependencies", _check_dependencies()),
        ("Ports", _check_port_availability()),
    ]

    for section_name, results in sections:
        all_results.extend(results)
        console.print()
        console.print(f"[bold]{section_name}[/bold]")
        for r in results:
            icon = _STATUS_ICONS[r.status]
            console.print(f"  {icon} {r.name}: {r.message}")

    # Summary
    counts = {"ok": 0, "warn": 0, "error": 0, "skip": 0}
    for r in all_results:
        counts[r.status] += 1

    console.print()

    table = Table(title="Summary", show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("[green]Passed[/green]", str(counts["ok"]))
    table.add_row("[yellow]Warnings[/yellow]", str(counts["warn"]))
    table.add_row("[red]Errors[/red]", str(counts["error"]))
    if counts["skip"]:
        table.add_row("[dim]Skipped[/dim]", str(counts["skip"]))
    console.print(table)

    if counts["error"] > 0:
        logger.debug("Doctor found {} error(s)", counts["error"])
        raise typer.Exit(code=1)
