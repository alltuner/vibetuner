import inspect
from functools import partial, wraps

import asyncer
import typer
from rich.console import Console

from core.config import project_settings
from core.logging import LogLevel, setup_logging


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


app = AsyncTyper(help=f"{project_settings.project_name.title()} CLI")

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
