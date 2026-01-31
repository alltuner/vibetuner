# ABOUTME: Run commands for starting the application in different modes
# ABOUTME: Supports dev/prod modes for frontend and worker services
import atexit
import signal
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console

from vibetuner.logging import logger
from vibetuner.paths import paths
from vibetuner.utils import compute_auto_port


console = Console()

PORT_FILE = Path(".vibetuner-port")


def _write_port_file(port: int) -> None:
    """Write the port number to .vibetuner-port file for dev mode."""
    PORT_FILE.write_text(str(port))


def _cleanup_port_file() -> None:
    """Remove the .vibetuner-port file on shutdown."""
    PORT_FILE.unlink(missing_ok=True)


def _setup_port_file_cleanup() -> None:
    """Register cleanup handlers for the port file."""
    atexit.register(_cleanup_port_file)

    def signal_handler(signum, frame):
        _cleanup_port_file()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


run_app = typer.Typer(
    help="Run the application in different modes", no_args_is_help=True
)

DEFAULT_FRONTEND_PORT = 8000
DEFAULT_WORKER_PORT = 11111


def _run_worker(mode: Literal["dev", "prod"], port: int, workers: int) -> None:
    """Start the background worker process."""
    from streaq.cli import main as streaq_main

    from vibetuner.config import settings

    if not settings.workers_available:
        logger.warning("Redis URL not configured. Workers will not be started.")
        console.print(
            "[red]Error: Redis URL not configured. Workers will not be started.[/red]"
        )
        raise typer.Exit(code=0)

    is_dev = mode == "dev"

    if is_dev and workers > 1:
        console.print(
            "[yellow]Warning: Multiple workers not supported in dev mode, using 1[/yellow]"
        )
        workers = 1

    console.print(f"[green]Starting worker in {mode} mode on port {port}[/green]")
    if is_dev:
        console.print("[dim]Hot reload enabled[/dim]")
    else:
        console.print(f"[dim]Workers: {workers}[/dim]")

    streaq_main(
        worker_path="vibetuner.tasks.worker.worker",
        workers=workers,
        reload=is_dev,
        verbose=True if is_dev else settings.debug,
        web=True,
        host="0.0.0.0",  # noqa: S104
        port=port,
    )


def _run_frontend(
    mode: Literal["dev", "prod"], host: str, port: int, workers: int
) -> None:
    """Start the frontend server."""
    from granian import Granian
    from granian.constants import Interfaces

    is_dev = mode == "dev"

    if is_dev:
        _write_port_file(port)
        _setup_port_file_cleanup()

    console.print(f"[green]Starting frontend in {mode} mode on {host}:{port}[/green]")
    console.print(f"[cyan]website reachable at http://localhost:{port}[/cyan]")
    console.print(
        f"[cyan]website reachable at https://{port}.localdev.alltuner.com:12000/[/cyan]"
    )
    if is_dev:
        console.print("[dim]Watching for changes in src/ and templates/[/dim]")
    else:
        console.print(f"[dim]Workers: {workers}[/dim]")

    print(paths.reload_paths)

    server = Granian(
        target="vibetuner.frontend.proxy:app",
        address=host,
        port=port,
        interface=Interfaces.ASGI,
        workers=workers,
        reload=is_dev,
        reload_paths=paths.reload_paths if is_dev else [],
        log_level="info",
        log_access=True,
    )

    server.serve()


def _run_service(
    mode: Literal["dev", "prod"],
    service: str,
    host: str,
    port: int | None,
    workers: int,
) -> None:
    """Dispatch to the appropriate service runner."""
    if service == "worker":
        _run_worker(mode, port or DEFAULT_WORKER_PORT, workers)
    elif service == "frontend":
        _run_frontend(mode, host, port or DEFAULT_FRONTEND_PORT, workers)
    else:
        console.print(f"[red]Error: Unknown service '{service}'[/red]")
        console.print("[yellow]Valid services: 'frontend' or 'worker'[/yellow]")
        raise typer.Exit(code=1)


@run_app.command(name="dev")
def dev(
    service: Annotated[
        str, typer.Argument(help="Service to run: 'frontend' or 'worker'")
    ] = "frontend",
    port: int | None = typer.Option(
        None, help="Port to run on (8000 for frontend, 11111 for worker)"
    ),
    auto_port: bool = typer.Option(
        False,
        "--auto-port",
        help="Use deterministic port based on project path (8001-8999)",
    ),
    host: str = typer.Option("0.0.0.0", help="Host to bind to (frontend only)"),  # noqa: S104
    workers_count: int = typer.Option(
        1, "--workers", help="Number of worker processes"
    ),
) -> None:
    """Run in development mode with hot reload (frontend or worker)."""
    if port is not None and auto_port:
        console.print("[red]Error: --port and --auto-port are mutually exclusive[/red]")
        raise typer.Exit(code=1)

    if auto_port:
        port = compute_auto_port()

    _run_service("dev", service, host, port, workers_count)


@run_app.command(name="prod")
def prod(
    service: Annotated[
        str, typer.Argument(help="Service to run: 'frontend' or 'worker'")
    ] = "frontend",
    port: int = typer.Option(
        None, help="Port to run on (8000 for frontend, 11111 for worker)"
    ),
    host: str = typer.Option("0.0.0.0", help="Host to bind to (frontend only)"),  # noqa: S104
    workers_count: int = typer.Option(
        4, "--workers", help="Number of worker processes"
    ),
) -> None:
    """Run in production mode (frontend or worker)."""
    _run_service("prod", service, host, port, workers_count)
