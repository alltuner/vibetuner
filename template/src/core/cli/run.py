# ABOUTME: Run commands for starting the application in different modes
# ABOUTME: Supports dev/prod modes for frontend and worker services
import os

import typer
from rich.console import Console


console = Console()

run_app = typer.Typer(
    help="Run the application in different modes", no_args_is_help=True
)


@run_app.command(name="dev")
def dev(
    worker: bool = typer.Option(False, "--worker", help="Run worker instead of frontend"),
    port: int = typer.Option(None, help="Port to run on (8000 for frontend, 11111 for worker)"),
    host: str = typer.Option("0.0.0.0", help="Host to bind to (frontend only)"),  # noqa: S104
    workers_count: int = typer.Option(1, "--workers", help="Number of worker processes"),
) -> None:
    """Run in development mode with hot reload (frontend or worker)."""
    os.environ["DEBUG"] = "1"

    if worker:
        # Worker mode
        from streaq.cli import main as streaq_main

        worker_port = port if port else 11111
        console.print(f"[green]Starting worker in dev mode on port {worker_port}[/green]")
        console.print("[dim]Hot reload enabled[/dim]")

        if workers_count > 1:
            console.print("[yellow]Warning: Multiple workers not supported in dev mode, using 1[/yellow]")

        # Call streaq programmatically
        streaq_main(
            worker_path="core.tasks.worker.worker",
            workers=1,
            reload=True,
            verbose=True,
            web=True,
            host="0.0.0.0",  # noqa: S104
            port=worker_port,
        )
    else:
        # Frontend mode
        from pathlib import Path

        from granian import Granian
        from granian.constants import Interfaces

        frontend_port = port if port else 8000
        console.print(f"[green]Starting frontend in dev mode on {host}:{frontend_port}[/green]")
        console.print("[dim]Watching for changes in src/ and templates/[/dim]")

        # Define paths to watch for changes
        reload_paths = [
            Path("src/core"),
            Path("src/app"),
            Path("templates/core/frontend"),
            Path("templates/app/frontend"),
        ]

        server = Granian(
            target="core.frontend:app",
            address=host,
            port=frontend_port,
            interface=Interfaces.ASGI,
            workers=workers_count,
            reload=True,
            reload_paths=reload_paths,
            log_level="info",
            log_access=True,
        )

        server.serve()


@run_app.command(name="prod")
def prod(
    worker: bool = typer.Option(False, "--worker", help="Run worker instead of frontend"),
    port: int = typer.Option(None, help="Port to run on (8000 for frontend, 11111 for worker)"),
    host: str = typer.Option("0.0.0.0", help="Host to bind to (frontend only)"),  # noqa: S104
    workers_count: int = typer.Option(4, "--workers", help="Number of worker processes"),
) -> None:
    """Run in production mode (frontend or worker)."""
    os.environ["ENVIRONMENT"] = "production"

    if worker:
        # Worker mode
        from streaq.cli import main as streaq_main

        worker_port = port if port else 11111
        console.print(f"[green]Starting worker in prod mode on port {worker_port}[/green]")
        console.print(f"[dim]Workers: {workers_count}[/dim]")

        # Call streaq programmatically
        streaq_main(
            worker_path="core.tasks.worker.worker",
            workers=workers_count,
            reload=False,
            verbose=False,
            web=True,
            host="0.0.0.0",  # noqa: S104
            port=worker_port,
        )
    else:
        # Frontend mode
        from granian import Granian
        from granian.constants import Interfaces

        frontend_port = port if port else 8000
        console.print(f"[green]Starting frontend in prod mode on {host}:{frontend_port}[/green]")
        console.print(f"[dim]Workers: {workers_count}[/dim]")

        server = Granian(
            target="core.frontend:app",
            address=host,
            port=frontend_port,
            interface=Interfaces.ASGI,
            workers=workers_count,
            reload=False,
            log_level="info",
            log_access=True,
        )

        server.serve()
