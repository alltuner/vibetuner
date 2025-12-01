# ABOUTME: Database management CLI commands for SQLModel.
# ABOUTME: Provides schema creation and other database utilities.

import asyncer
import typer


db_app = typer.Typer(help="Database management commands", no_args_is_help=True)


@db_app.command("create-schema")
def create_schema_cmd() -> None:
    """
    Create database tables from SQLModel metadata.

    This command creates all tables defined in your SQLModel models.
    It's idempotent - existing tables are not modified.

    Run this during initial setup or after adding new models.
    """
    from importlib import import_module

    from vibetuner.logging import logger

    # Import app.models to register SQLModel tables before schema creation
    try:
        import_module("app.models")
    except ModuleNotFoundError:
        logger.warning("app.models not found. Only core models will be created.")
    except ImportError as e:
        logger.warning(f"Failed to import app.models: {e}")

    async def _create() -> None:
        from vibetuner.sqlmodel import create_schema

        await create_schema()

    typer.echo("Creating database schema...")
    asyncer.runnify(_create)()
    typer.echo("Database schema created successfully.")
