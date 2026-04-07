# ABOUTME: CLI commands for managing runtime config values.
# ABOUTME: Provides list, set, and delete for config entries including secrets.
from typing import Annotated

import typer

from vibetuner.mongo import init_mongodb
from vibetuner.runtime_config import RuntimeConfig


config_app = typer.Typer(
    help="Manage runtime configuration values", no_args_is_help=True
)


async def _list_impl() -> None:
    from rich.console import Console
    from rich.table import Table

    from vibetuner.loader import load_app_config

    load_app_config()
    await init_mongodb()
    await RuntimeConfig.refresh_cache()

    entries = await RuntimeConfig.get_all_config()

    if not entries:
        typer.echo("No config values registered.")
        return

    console = Console()
    table = Table(title="Runtime Configuration")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Source", style="magenta")
    table.add_column("Category", style="blue")

    for entry in entries:
        if entry["is_secret"]:
            display_value = "********" if entry["source"] != "default" else "(not set)"
        else:
            display_value = str(entry["value"])

        table.add_row(
            entry["key"],
            display_value,
            entry["value_type"],
            entry["source"],
            entry["category"],
        )

    console.print(table)


async def _set_impl(key: str, value: str | None) -> None:
    from vibetuner.loader import load_app_config

    load_app_config()
    await init_mongodb()

    if key not in RuntimeConfig._config_registry:
        typer.echo(f"Error: Key '{key}' is not registered.", err=True)
        raise typer.Exit(1)

    entry = RuntimeConfig._config_registry[key]
    is_secret = entry["is_secret"]

    if value is not None and is_secret:
        typer.echo(
            "Warning: Secret value passed as argument. It may appear in shell history.",
            err=True,
        )
    elif value is None:
        if is_secret:
            value = typer.prompt("Value", hide_input=True)
        else:
            value = typer.prompt("Value")

    await RuntimeConfig.set_value(
        key=key,
        value=value,
        value_type=entry["value_type"],
        description=entry["description"],
        category=entry["category"],
        is_secret=is_secret,
    )

    typer.echo(f"Set '{key}' successfully.")


async def _delete_impl(key: str, yes: bool) -> None:
    from vibetuner.loader import load_app_config

    load_app_config()
    await init_mongodb()

    if key not in RuntimeConfig._config_registry:
        typer.echo(f"Error: Key '{key}' is not registered.", err=True)
        raise typer.Exit(1)

    if not yes:
        confirmed = typer.confirm(f"Delete config value '{key}' from MongoDB?")
        if not confirmed:
            typer.echo("Aborted.")
            return

    deleted = await RuntimeConfig.delete_value(key)
    if deleted:
        typer.echo(f"Deleted '{key}' from MongoDB.")
    else:
        typer.echo(f"Value for '{key}' not found in MongoDB (only default exists).")


@config_app.command("list")
def config_list() -> None:
    """List all registered config keys, their values, and sources."""
    import asyncer

    asyncer.runnify(_list_impl)()


@config_app.command("set")
def config_set(
    key: Annotated[
        str, typer.Argument(help="Config key to set (e.g. secrets.api_key)")
    ],
    value: Annotated[
        str | None,
        typer.Option(
            "--value",
            "-v",
            help="Value to set. Omit for secrets to use hidden prompt.",
        ),
    ] = None,
) -> None:
    """Set a config value. Secrets use a hidden prompt by default."""
    import asyncer

    asyncer.runnify(_set_impl)(key, value)


@config_app.command("delete")
def config_delete(
    key: Annotated[str, typer.Argument(help="Config key to delete from MongoDB")],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Delete a config value from MongoDB (reverts to default)."""
    import asyncer

    asyncer.runnify(_delete_impl)(key, yes)
