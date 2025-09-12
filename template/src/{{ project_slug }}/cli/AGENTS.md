
# CLI Module

Command-line interface using AsyncTyper.

## Structure

- `__init__.py` - CLI app initialization and command registration
- `_helper.py` - Shared utilities for CLI commands
- Add your custom commands as new files here

## Command Pattern

Use AsyncTyper for all CLI commands:

```python
from asynctyper import AsyncTyper
from typing import Optional
import asyncio

app = AsyncTyper()

@app.command()
async def my_command(
    name: str,
    count: int = 1,
    verbose: bool = False
):
    """Process items with async support."""
    for i in range(count):
        await process_item(name, i)
        if verbose:
            print(f"Processed {name} #{i}")

# Register in __init__.py
from .my_commands import app as my_app
main_app.add_typer(my_app, name="my-commands")
```

## Running Commands

```bash
# Via uv (recommended)
uv run python -m [project_slug] my-command --name test --count 5

# After installation
[project_slug] my-command --name test --count 5
```

## Database Commands

Access MongoDB in commands:

```python
from ..core.mongo import init_mongo, close_mongo
from ..models import User

@app.command()
async def list_users():
    """List all users in database."""
    await init_mongo()
    try:
        users = await User.find_all().to_list()
        for user in users:
            print(f"{user.email} - {user.db_insert_dt}")
    finally:
        await close_mongo()
```

## Common Patterns

### Progress Bars

```python
from rich.progress import track

@app.command()
async def process_files(directory: str):
    files = list(Path(directory).glob("*.txt"))
    for file in track(files, description="Processing..."):
        await process_file(file)
```

### Confirmation Prompts

```python
from typer import confirm

@app.command()
async def dangerous_operation():
    if not confirm("Are you sure?"):
        raise typer.Abort()
    await perform_operation()
```

### Output Formatting

```python
from rich.console import Console
from rich.table import Table

console = Console()

@app.command()
async def show_stats():
    table = Table(title="Statistics")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Users", "1234")
    console.print(table)
```

## Package Management

```bash
uv add asynctyper rich      # Add CLI dependencies
uv sync                     # Sync dependencies
uv run python -m [project_slug] --help  # Show CLI help
```