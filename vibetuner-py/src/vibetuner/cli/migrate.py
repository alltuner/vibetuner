# ABOUTME: MongoDB schema migration CLI commands.
# ABOUTME: Provides create/up/down/status commands for managing MongoDB migrations.
from datetime import datetime
from pathlib import Path
from typing import Annotated

import asyncer
import typer
from rich.console import Console
from rich.table import Table


console = Console()

migrate_app = typer.Typer(
    help="MongoDB migration management commands", no_args_is_help=True
)


def _get_migrations_dir() -> Path:
    """Get the migrations directory, creating it if needed."""
    from vibetuner.paths import root

    if root is None:
        console.print("[red]Error: Not in a vibetuner project directory.[/red]")
        raise typer.Exit(code=1)

    migrations_dir = root / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    return migrations_dir


def _generate_migration_filename(name: str) -> str:
    """Generate a timestamped migration filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = name.lower().replace(" ", "_").replace("-", "_")
    # Strip non-alphanumeric except underscores
    slug = "".join(c for c in slug if c.isalnum() or c == "_")
    return f"{timestamp}_{slug}.py"


def _discover_migrations(migrations_dir: Path) -> list[Path]:
    """Discover migration files sorted by filename (chronological)."""
    files = sorted(migrations_dir.glob("*.py"))
    return [f for f in files if not f.name.startswith("__")]


MIGRATION_TEMPLATE = '''"""Migration: {name}

Created: {timestamp}
"""

from pymongo.asynchronous.database import AsyncDatabase


async def up(db: AsyncDatabase) -> None:
    """Apply this migration."""
    # Example operations:
    # await db["collection"].create_index("field_name")
    # await db["collection"].update_many({{}}, {{"$set": {{"new_field": "default"}}}})
    pass


async def down(db: AsyncDatabase) -> None:
    """Reverse this migration."""
    # Undo the operations performed in up()
    # await db["collection"].drop_index("field_name_1")
    # await db["collection"].update_many({{}}, {{"$unset": {{"new_field": ""}}}})
    pass
'''


@migrate_app.command("create")
def create(
    name: Annotated[str, typer.Argument(help="Name describing the migration")],
) -> None:
    """Create a new migration file."""
    migrations_dir = _get_migrations_dir()
    filename = _generate_migration_filename(name)
    filepath = migrations_dir / filename

    content = MIGRATION_TEMPLATE.format(
        name=name,
        timestamp=datetime.now().isoformat(),
    )

    filepath.write_text(content, encoding="utf-8")
    console.print(
        f"[green]Created migration:[/green] {filepath.relative_to(migrations_dir.parent)}"
    )


@migrate_app.command("up")
def up(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show which migrations would run without applying them"
    ),
) -> None:
    """Apply all pending migrations."""
    migrations_dir = _get_migrations_dir()

    async def _run() -> None:
        from vibetuner.migrations import apply_pending_migrations

        applied = await apply_pending_migrations(migrations_dir, dry_run=dry_run)
        if not applied:
            console.print("[dim]No pending migrations.[/dim]")
        elif dry_run:
            console.print(
                f"\n[yellow]Dry run: {len(applied)} migration(s) would be applied.[/yellow]"
            )
        else:
            console.print(
                f"\n[green]{len(applied)} migration(s) applied successfully.[/green]"
            )

    asyncer.runnify(_run)()


@migrate_app.command("down")
def down(
    steps: int = typer.Option(
        1, "--steps", "-n", help="Number of migrations to roll back"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show which migrations would be rolled back"
    ),
) -> None:
    """Roll back the most recent migration(s)."""
    migrations_dir = _get_migrations_dir()

    async def _run() -> None:
        from vibetuner.migrations import rollback_migrations

        rolled_back = await rollback_migrations(
            migrations_dir, steps=steps, dry_run=dry_run
        )
        if not rolled_back:
            console.print("[dim]No migrations to roll back.[/dim]")
        elif dry_run:
            console.print(
                f"\n[yellow]Dry run: {len(rolled_back)} migration(s) would be rolled back.[/yellow]"
            )
        else:
            console.print(
                f"\n[green]{len(rolled_back)} migration(s) rolled back successfully.[/green]"
            )

    asyncer.runnify(_run)()


@migrate_app.command("status")
def status() -> None:
    """Show migration status."""
    migrations_dir = _get_migrations_dir()

    async def _run() -> None:
        from vibetuner.migrations import get_migration_status

        statuses = await get_migration_status(migrations_dir)

        if not statuses:
            console.print("[dim]No migrations found.[/dim]")
            return

        table = Table(title="Migration Status")
        table.add_column("Migration", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Applied At", style="dim")

        for entry in statuses:
            status_str = (
                "[green]applied[/green]"
                if entry["applied"]
                else "[yellow]pending[/yellow]"
            )
            applied_at = entry.get("applied_at", "")
            if applied_at and isinstance(applied_at, datetime):
                applied_at = applied_at.strftime("%Y-%m-%d %H:%M:%S")
            table.add_row(
                entry["name"], status_str, str(applied_at) if applied_at else ""
            )

        console.print(table)

    asyncer.runnify(_run)()
