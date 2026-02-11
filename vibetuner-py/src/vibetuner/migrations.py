# ABOUTME: MongoDB migration engine for applying and rolling back schema changes.
# ABOUTME: Tracks migration history in a _migrations collection.
from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from vibetuner.logging import logger


MIGRATIONS_COLLECTION = "_migrations"


async def _get_db():
    """Get the MongoDB database instance."""
    from vibetuner.config import settings
    from vibetuner.mongo import _ensure_client, mongo_client

    _ensure_client()
    if mongo_client is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGODB_URL to use migrations."
        )
    return mongo_client[settings.mongo_dbname]


def _load_migration_module(filepath: Path):
    """Dynamically load a migration file as a Python module."""
    spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load migration: {filepath}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _discover_migrations(migrations_dir: Path) -> list[Path]:
    """Discover migration files sorted by filename (chronological)."""
    files = sorted(migrations_dir.glob("*.py"))
    return [f for f in files if not f.name.startswith("__")]


async def _get_applied_migrations(db) -> dict[str, Any]:
    """Get all applied migrations from the _migrations collection."""
    collection = db[MIGRATIONS_COLLECTION]
    applied = {}
    async for doc in collection.find().sort("applied_at", 1):
        applied[doc["name"]] = doc
    return applied


async def apply_pending_migrations(
    migrations_dir: Path, *, dry_run: bool = False
) -> list[str]:
    """Apply all pending migrations in order.

    Args:
        migrations_dir: Path to the migrations directory.
        dry_run: If True, only report what would be applied.

    Returns:
        List of migration names that were applied (or would be applied).
    """
    from rich.console import Console

    console = Console()
    db = await _get_db()
    applied = await _get_applied_migrations(db)
    migration_files = _discover_migrations(migrations_dir)

    pending = [f for f in migration_files if f.stem not in applied]
    if not pending:
        return []

    applied_names: list[str] = []
    for filepath in pending:
        name = filepath.stem
        if dry_run:
            console.print(f"  [yellow]Would apply:[/yellow] {name}")
            applied_names.append(name)
            continue

        console.print(f"  [cyan]Applying:[/cyan] {name} ... ", end="")
        module = _load_migration_module(filepath)

        if not hasattr(module, "up"):
            console.print("[red]SKIP (no up() function)[/red]")
            continue

        try:
            await module.up(db)
            # Record in _migrations collection
            await db[MIGRATIONS_COLLECTION].insert_one(
                {
                    "name": name,
                    "applied_at": datetime.now(UTC),
                }
            )
            console.print("[green]OK[/green]")
            applied_names.append(name)
            logger.info("Applied migration: {}", name)
        except Exception as e:
            console.print(f"[red]FAILED: {e}[/red]")
            logger.error("Migration {} failed: {}", name, e)
            raise

    return applied_names


async def rollback_migrations(
    migrations_dir: Path, *, steps: int = 1, dry_run: bool = False
) -> list[str]:
    """Roll back the most recent migrations.

    Args:
        migrations_dir: Path to the migrations directory.
        steps: Number of migrations to roll back.
        dry_run: If True, only report what would be rolled back.

    Returns:
        List of migration names that were rolled back (or would be).
    """
    from rich.console import Console

    console = Console()
    db = await _get_db()
    collection = db[MIGRATIONS_COLLECTION]

    # Get applied migrations in reverse chronological order
    applied_docs = []
    async for doc in collection.find().sort("applied_at", -1).limit(steps):
        applied_docs.append(doc)

    if not applied_docs:
        return []

    migration_files = {f.stem: f for f in _discover_migrations(migrations_dir)}
    rolled_back: list[str] = []

    for doc in applied_docs:
        name = doc["name"]
        if dry_run:
            console.print(f"  [yellow]Would roll back:[/yellow] {name}")
            rolled_back.append(name)
            continue

        filepath = migration_files.get(name)
        if filepath is None:
            console.print(f"  [red]Migration file not found:[/red] {name}")
            continue

        console.print(f"  [cyan]Rolling back:[/cyan] {name} ... ", end="")
        module = _load_migration_module(filepath)

        if not hasattr(module, "down"):
            console.print("[red]SKIP (no down() function)[/red]")
            continue

        try:
            await module.down(db)
            await collection.delete_one({"name": name})
            console.print("[green]OK[/green]")
            rolled_back.append(name)
            logger.info("Rolled back migration: {}", name)
        except Exception as e:
            console.print(f"[red]FAILED: {e}[/red]")
            logger.error("Rollback of {} failed: {}", name, e)
            raise

    return rolled_back


async def get_migration_status(migrations_dir: Path) -> list[dict[str, Any]]:
    """Get the status of all migrations.

    Returns:
        List of dicts with 'name', 'applied', and optionally 'applied_at' keys.
    """
    db = await _get_db()
    applied = await _get_applied_migrations(db)
    migration_files = _discover_migrations(migrations_dir)

    statuses: list[dict[str, Any]] = []
    for filepath in migration_files:
        name = filepath.stem
        if name in applied:
            statuses.append(
                {
                    "name": name,
                    "applied": True,
                    "applied_at": applied[name].get("applied_at"),
                }
            )
        else:
            statuses.append({"name": name, "applied": False, "applied_at": None})

    return statuses
