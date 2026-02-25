# ABOUTME: Run commands for starting the application in different modes
# ABOUTME: Supports dev/prod modes for frontend and worker services
from typing import Annotated, Literal

import typer
from rich.console import Console

from vibetuner.paths import paths


console = Console()

run_app = typer.Typer(
    help="Run the application in different modes", no_args_is_help=True
)


def _run_worker(mode: Literal["dev", "prod"], port: int, workers: int) -> None:
    """Start the background worker process with monitoring web UI."""
    from multiprocessing import Process

    from streaq.cli import run_worker
    from streaq.ui import run_web

    from vibetuner.config import settings

    if not settings.workers_available:
        from vibetuner.services.errors import redis_not_configured

        redis_not_configured()
        raise typer.Exit(code=1)

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

    worker_path = "vibetuner.tasks.worker:worker"
    verbose = True if is_dev else settings.debug

    # Start monitoring web UI and additional workers as background processes
    web_host = "0.0.0.0"  # noqa: S104
    processes: list[Process] = []

    web_process = Process(target=run_web, args=(web_host, port, worker_path))
    web_process.start()
    processes.append(web_process)

    for _ in range(workers - 1):
        p = Process(target=run_worker, args=(worker_path, False, is_dev, verbose))
        p.start()
        processes.append(p)

    # Run main worker in the current process (blocks)
    try:
        run_worker(worker_path, False, is_dev, verbose)
    finally:
        for p in processes:
            p.terminate()
            p.join(timeout=5)


def _run_frontend(
    mode: Literal["dev", "prod"], host: str, port: int, workers: int
) -> None:
    """Start the frontend server."""
    from granian import Granian
    from granian.constants import Interfaces

    is_dev = mode == "dev"

    console.print(f"[green]Starting frontend in {mode} mode on {host}:{port}[/green]")
    console.print(f"[cyan]website reachable at http://localhost:{port}[/cyan]")

    if is_dev:
        console.print("[dim]Watching for changes in src/ and templates/[/dim]")
    else:
        console.print(f"[dim]Workers: {workers}[/dim]")

    console.print("Registered reload paths:")
    for path in paths.reload_paths:
        console.print(f"  - {path}")

    server = Granian(
        target="vibetuner.frontend.proxy:app",
        address=host,
        port=port,
        interface=Interfaces.ASGI,
        workers=workers,
        workers_kill_timeout=5,
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
    from vibetuner.config import settings

    if service == "worker":
        _run_worker(mode, port or settings.resolved_worker_port, workers)
    elif service == "frontend":
        _run_frontend(mode, host, port or settings.resolved_port, workers)
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
        None, help="Port to run on (auto-calculated if not specified)"
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
        None, help="Port to run on (8000 if not specified)"
    ),
    host: str = typer.Option("0.0.0.0", help="Host to bind to (frontend only)"),  # noqa: S104
    workers_count: int = typer.Option(
        4, "--workers", help="Number of worker processes"
    ),
) -> None:
    """Run in production mode (frontend or worker)."""
    _run_service("prod", service, host, port, workers_count)
