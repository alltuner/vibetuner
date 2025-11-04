# ABOUTME: Core CLI setup with AsyncTyper wrapper and base configuration
# ABOUTME: Provides main CLI entry point and logging configuration
import inspect
from functools import partial, wraps
from importlib import import_module

import asyncer
import typer
from rich.console import Console

from vibetuner.cli.run import run_app
from vibetuner.cli.scaffold import scaffold_app
from vibetuner.config import settings
from vibetuner.logging import LogLevel, setup_logging


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


app = AsyncTyper(help=f"{settings.project.project_name.title()} CLI")

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


app.add_typer(run_app, name="run")
app.add_typer(scaffold_app, name="scaffold")

try:
    import_module("app.cli")
except (ImportError, ModuleNotFoundError):
    pass
