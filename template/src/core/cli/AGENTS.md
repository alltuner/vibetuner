# CLI Module

Command-line interface using AsyncTyper.

## Quick Reference

- `__init__.py` - CLI app initialization
- `_helper.py` - Shared utilities
- Add your custom commands as new files

## Command Pattern

```python
from asynctyper import AsyncTyper

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

## Running

```bash
uv run [project_slug] my-command --name test --count 5
# Or after install:
[project_slug] my-command --name test
```

## Database Access

```python
from ..core.mongo import init_mongo
from ..models import User

@app.command()
async def list_users():
    """List all users."""
    await init_mongo()
    users = await User.find_all().to_list()
    for user in users:
        print(f"{user.email} - {user.db_insert_dt}")
```

## Common Patterns

### Progress Bars

```python
from rich.progress import track

for file in track(files, description="Processing..."):
    await process_file(file)
```

### Tables

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Statistics")
table.add_column("Metric")
table.add_column("Value")
table.add_row("Users", "1234")
console.print(table)
```
