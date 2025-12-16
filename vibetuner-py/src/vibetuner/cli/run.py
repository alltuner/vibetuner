# ABOUTME: Run commands for starting the application in different modes
# ABOUTME: Supports dev/prod modes for frontend and worker services
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console

from vibetuner.logging import logger


console = Console()

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

    console.print(f"[green]Starting frontend in {mode} mode on {host}:{port}[/green]")
    if is_dev:
        console.print("[dim]Watching for changes in src/ and templates/[/dim]")
    else:
        console.print(f"[dim]Workers: {workers}[/dim]")

    reload_paths = (
        [
            Path("src/app"),
            Path("templates/frontend"),
            Path("templates/email"),
            Path("templates/markdown"),
        ]
        if is_dev
        else None
    )

    server = Granian(
        target="vibetuner.frontend.proxy:app",
        address=host,
        port=port,
        interface=Interfaces.ASGI,
        workers=workers,
        reload=is_dev,
        reload_paths=reload_paths,
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
    port: int = typer.Option(
        None, help="Port to run on (8000 for frontend, 11111 for worker)"
    ),
    host: str = typer.Option("0.0.0.0", help="Host to bind to (frontend only)"),  # noqa: S104
    workers_count: int = typer.Option(
        1, "--workers", help="Number of worker processes"
    ),
) -> None:
    """Run in development mode with hot reload (frontend or worker)."""
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
