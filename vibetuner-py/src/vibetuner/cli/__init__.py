# ABOUTME: Core CLI setup with AsyncTyper wrapper and base configuration
# ABOUTME: Provides main CLI entry point and logging configuration
import importlib.metadata
import inspect
from functools import partial, wraps
from importlib import import_module
from pathlib import Path
from typing import Annotated

import asyncer
import typer
from rich.console import Console
from rich.table import Table

from vibetuner.cli.run import run_app
from vibetuner.cli.scaffold import scaffold_app
from vibetuner.logging import LogLevel, logger, setup_logging


console = Console()


class AsyncTyper(typer.Typer):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("no_args_is_help", True)
        super().__init__(*args, **kwargs)

    @staticmethod
    def maybe_run_async(decorator, f):
        if inspect.iscoroutinefunction(f):

            @wraps(f)
            def runner(*args, **kwargs):
                return asyncer.runnify(f)(*args, **kwargs)

            decorator(runner)
        else:
            decorator(f)
        return f

    def callback(self, *args, **kwargs):
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)


def _get_app_help():
    try:
        from vibetuner.config import settings

        return f"{settings.project.project_name.title()} CLI"
    except (RuntimeError, ImportError):
        return "Vibetuner CLI"


app = AsyncTyper(help=_get_app_help())

LOG_LEVEL_OPTION = typer.Option(
    LogLevel.INFO,
    "--log-level",
    "-l",
    case_sensitive=False,
    help="Set the logging level",
)


@app.callback()
def callback(log_level: LogLevel | None = LOG_LEVEL_OPTION) -> None:
    """Initialize logging and other global settings."""
    setup_logging(level=log_level)


@app.command()
def version(
    show_app: bool = typer.Option(
        False,
        "--app",
        "-a",
        help="Show app settings version even if not in a project directory",
    ),
) -> None:
    """Show version information."""
    try:
        # Get vibetuner package version
        vibetuner_version = importlib.metadata.version("vibetuner")
    except importlib.metadata.PackageNotFoundError:
        vibetuner_version = "unknown"

    # Create table for nice display
    table = Table(title="Version Information")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Version", style="green", no_wrap=True)

    # Always show vibetuner package version
    table.add_row("vibetuner package", vibetuner_version)

    # Show app version if requested or if in a project
    try:
        from vibetuner.config import CoreConfiguration

        settings = CoreConfiguration()
        table.add_row(f"{settings.project.project_name} settings", settings.version)
    except Exception:
        if show_app:
            table.add_row("app settings", "not in project directory")
        # else: don't show app version if not in project and not requested

    console.print(table)


@app.command()
def core_template_symlink(
    target: Annotated[
        Path,
        typer.Argument(
            help="Path where the 'core' symlink should be created or updated",
        ),
    ],
) -> None:
    """Create or update a 'core' symlink to the package templates directory."""
    from vibetuner.paths import create_core_templates_symlink

    create_core_templates_symlink(target)


app.add_typer(run_app, name="run")
app.add_typer(scaffold_app, name="scaffold")

try:
    import_module("app.cli")
except ModuleNotFoundError:
    # Silent pass for missing app.cli module (expected in some projects)
    pass
except ImportError as e:
    # Log warning for any import error (including syntax errors, missing dependencies, etc.)
    logger.warning(
        f"Failed to import app.cli: {e}. User CLI commands will not be available."
    )
