# ABOUTME: Core CLI setup with AsyncTyper wrapper and base configuration
# ABOUTME: Provides main CLI entry point and logging configuration
import importlib.metadata
import inspect
from functools import partial, wraps

import asyncer
import typer
from rich.console import Console
from rich.table import Table

from vibetuner.cli.db import db_app
from vibetuner.cli.doctor import doctor_app
from vibetuner.cli.run import run_app
from vibetuner.cli.scaffold import scaffold_app
from vibetuner.loader import ConfigurationError, load_app_config
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

        name = settings.project.project_name
        if name and name != "default_project":
            return f"{name.title()} CLI"
    except (RuntimeError, ImportError):
        pass

    try:
        from vibetuner.pyproject import get_project_name

        name = get_project_name()
        if name:
            return f"{name.replace('_', ' ').title()} CLI"
    except Exception:
        pass

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
def callback(
    ctx: typer.Context,
    log_level: LogLevel | None = LOG_LEVEL_OPTION,
) -> None:
    """Initialize logging and other global settings."""
    if ctx.resilient_parsing:
        return
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


app.add_typer(db_app, name="db")
app.add_typer(doctor_app, name="doctor")
app.add_typer(run_app, name="run")
app.add_typer(scaffold_app, name="scaffold")

# Add user CLI commands from tune.py
try:
    _app_config = load_app_config()
    if _app_config.cli:
        _user_cli = _app_config.cli
        # Determine the user-provided name, if any
        _user_name = getattr(getattr(_user_cli, "info", None), "name", None)
        # Collect core command/group names so we can detect shadowing
        _core_names = {
            cmd.name
            for cmd in app.registered_groups + app.registered_commands
            if hasattr(cmd, "name") and cmd.name
        }
        if _user_name and _user_name in _core_names:
            logger.warning(
                f"User CLI group name '{_user_name}' shadows a core vibetuner "
                f"command. Falling back to namespace 'app'."
            )
            _user_name = "app"
        # Guard against self-referencing cycle: if the user re-exported
        # vibetuner.cli.app instead of creating their own Typer instance,
        # adding it as a sub-group of itself causes infinite recursion in
        # typer >=0.23 (eager group hierarchy resolution).
        if _user_cli is app:
            logger.warning(
                "User CLI is the same object as vibetuner's root app. "
                "Skipping registration to avoid circular reference. "
                "Create a separate AsyncTyper() or typer.Typer() instance "
                "for your CLI commands instead of re-exporting vibetuner.cli.app."
            )
        else:
            # Ensure the user CLI is always namespaced to prevent top-level shadowing
            app.add_typer(_user_cli, name=_user_name or "app")
            logger.debug("Registered user CLI commands from tune.py")
except ConfigurationError:
    # Not in a project directory or tune.py misconfigured, skip user CLI
    pass
