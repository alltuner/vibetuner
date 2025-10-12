# Application CLI Commands

**YOUR CLI COMMANDS GO HERE** - Define command-line interface commands using Typer.

## What Goes Here

Create your application-specific CLI commands in this directory:

- Database management commands
- Data import/export utilities
- Administrative tasks
- Development utilities
- Maintenance scripts
- Any command-line tools for your application

## Command Pattern

```python
# commands.py
import typer
from core.models import UserModel
from core.mongo import init_db

app = typer.Typer(help="Application management commands")

@app.command()
def create_user(
    email: str = typer.Option(..., help="User email"),
    name: str = typer.Option(..., help="Display name"),
    admin: bool = typer.Option(False, help="Make user admin")
):
    """Create a new user account."""
    import asyncio

    async def _create():
        await init_db()

        # Check if exists
        existing = await UserModel.find_one(UserModel.email == email)
        if existing:
            typer.echo(f"❌ User {email} already exists", err=True)
            raise typer.Exit(1)

        # Create user
        user = UserModel(
            email=email,
            display_name=name,
            is_admin=admin
        )
        await user.insert()

        typer.echo(f"✅ Created user: {email}")
        typer.echo(f"   ID: {user.id}")
        typer.echo(f"   Admin: {admin}")

    asyncio.run(_create())

@app.command()
def list_users(
    limit: int = typer.Option(10, help="Max users to show")
):
    """List users in the database."""
    import asyncio

    async def _list():
        await init_db()

        users = await UserModel.find_all().limit(limit).to_list()

        if not users:
            typer.echo("No users found")
            return

        typer.echo(f"\n{'Email':<30} {'Name':<20} {'Admin'}")
        typer.echo("-" * 60)

        for user in users:
            admin_mark = "✓" if user.is_admin else ""
            typer.echo(f"{user.email:<30} {user.display_name:<20} {admin_mark}")

    asyncio.run(_list())
```

## Registering Commands

Update `__init__.py` to register your command groups:

```python
# __init__.py
import typer
from .commands import app as commands_app
from .import_data import app as import_app

# Main CLI app
cli = typer.Typer()

# Register command groups
cli.add_typer(commands_app, name="users")
cli.add_typer(import_app, name="import")
```

## Running Commands

### From Python Module

```bash
python -m src.app.cli users create-user --email=user@example.com --name="John Doe"
python -m src.app.cli users list-users --limit=20
```

### After Installation

If the package is installed, commands may be available directly (configured in pyproject.toml).

## Available from Core

### Database

```python
from core.mongo import init_db

async def command():
    await init_db()  # Initialize DB connection
    # Now you can use models
```

### Models

```python
from core.models import UserModel, OAuthAccountModel
from app.models.post import Post

# Access all models
```

### Configuration

```python
from core.config import project_settings
from app.config import settings

# Access configuration
```

## Common Patterns

### Database Operations

```python
@app.command()
def seed_data():
    """Seed database with test data."""
    import asyncio

    async def _seed():
        await init_db()

        # Create test users
        for i in range(10):
            user = UserModel(
                email=f"user{i}@example.com",
                display_name=f"User {i}"
            )
            await user.insert()

        typer.echo("✅ Seeded 10 test users")

    asyncio.run(_seed())

@app.command()
def clear_data(
    confirm: bool = typer.Option(False, "--yes", help="Skip confirmation")
):
    """Clear all data from database."""
    if not confirm:
        typer.confirm("⚠️  This will delete all data. Continue?", abort=True)

    import asyncio

    async def _clear():
        await init_db()

        # Delete all
        await UserModel.delete_all()

        typer.echo("✅ Cleared all data")

    asyncio.run(_clear())
```

### Data Import/Export

```python
import json
from pathlib import Path

@app.command()
def export_users(
    output: Path = typer.Argument(..., help="Output JSON file")
):
    """Export users to JSON file."""
    import asyncio

    async def _export():
        await init_db()

        users = await UserModel.find_all().to_list()

        data = [
            {
                "email": user.email,
                "name": user.display_name,
                "admin": user.is_admin
            }
            for user in users
        ]

        output.write_text(json.dumps(data, indent=2))
        typer.echo(f"✅ Exported {len(users)} users to {output}")

    asyncio.run(_export())

@app.command()
def import_users(
    input: Path = typer.Argument(..., help="Input JSON file", exists=True)
):
    """Import users from JSON file."""
    import asyncio

    async def _import():
        await init_db()

        data = json.loads(input.read_text())

        count = 0
        for item in data:
            existing = await UserModel.find_one(
                UserModel.email == item["email"]
            )
            if existing:
                typer.echo(f"⏭  Skipping {item['email']} (exists)")
                continue

            user = UserModel(
                email=item["email"],
                display_name=item["name"],
                is_admin=item.get("admin", False)
            )
            await user.insert()
            count += 1

        typer.echo(f"✅ Imported {count} users")

    asyncio.run(_import())
```

### Maintenance Tasks

```python
from datetime import datetime, timedelta

@app.command()
def cleanup_old_sessions():
    """Remove expired sessions."""
    import asyncio

    async def _cleanup():
        await init_db()

        cutoff = datetime.now() - timedelta(days=30)

        # Delete old sessions
        result = await Session.find(
            Session.expires_at < cutoff
        ).delete()

        typer.echo(f"✅ Deleted {result.deleted_count} expired sessions")

    asyncio.run(_cleanup())

@app.command()
def rebuild_indexes():
    """Rebuild database indexes."""
    import asyncio

    async def _rebuild():
        await init_db()

        # Get database
        from motor.motor_asyncio import AsyncIOMotorClient
        from core.config import project_settings

        client = AsyncIOMotorClient(str(project_settings.mongodb_url))
        db = client[project_settings.project_slug]

        # Rebuild indexes for each collection
        collections = await db.list_collection_names()

        for collection_name in collections:
            collection = db[collection_name]
            await collection.reindex()
            typer.echo(f"✅ Rebuilt indexes for {collection_name}")

    asyncio.run(_rebuild())
```

### Interactive Commands

```python
@app.command()
def interactive_user_create():
    """Create user interactively."""
    import asyncio

    email = typer.prompt("Email")
    name = typer.prompt("Display name")
    admin = typer.confirm("Make admin?", default=False)

    if not typer.confirm(f"Create user {email}?"):
        typer.echo("Cancelled")
        raise typer.Exit()

    async def _create():
        await init_db()

        user = UserModel(
            email=email,
            display_name=name,
            is_admin=admin
        )
        await user.insert()

        typer.echo(f"✅ Created user: {user.id}")

    asyncio.run(_create())
```

### Progress Bars

```python
from rich.progress import track

@app.command()
def process_all_users():
    """Process all users with progress bar."""
    import asyncio

    async def _process():
        await init_db()

        users = await UserModel.find_all().to_list()

        for user in track(users, description="Processing users..."):
            # Do something with each user
            await process_user(user)

        typer.echo("✅ Processed all users")

    asyncio.run(_process())
```

### Rich Output

```python
from rich.console import Console
from rich.table import Table

console = Console()

@app.command()
def show_stats():
    """Show database statistics."""
    import asyncio

    async def _stats():
        await init_db()

        user_count = await UserModel.count()
        post_count = await Post.count()

        table = Table(title="Database Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta")

        table.add_row("Users", str(user_count))
        table.add_row("Posts", str(post_count))

        console.print(table)

    asyncio.run(_stats())
```

## Command Organization

### Group Related Commands

```text
cli/
├── __init__.py          # Main CLI entry point
├── users.py             # User management commands
├── posts.py             # Post management commands
├── import_export.py     # Data import/export
└── maintenance.py       # Maintenance tasks
```

### Use Command Groups

```python
# users.py
import typer

app = typer.Typer(help="User management commands")

@app.command()
def create(...):
    """Create a user."""
    pass

@app.command()
def delete(...):
    """Delete a user."""
    pass

# __init__.py
cli = typer.Typer()
cli.add_typer(users_app, name="users")
cli.add_typer(posts_app, name="posts")
```

## Error Handling

```python
@app.command()
def dangerous_operation():
    """Dangerous operation."""
    try:
        # Do something
        pass
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def safe_operation():
    """Safe operation with validation."""
    if not validate_preconditions():
        typer.echo("❌ Preconditions not met", err=True)
        raise typer.Exit(1)

    # Continue...
```

## Testing CLI Commands

```python
from typer.testing import CliRunner
from app.cli import cli

runner = CliRunner()

def test_create_user():
    result = runner.invoke(
        cli,
        ["users", "create-user", "--email=test@example.com", "--name=Test"]
    )
    assert result.exit_code == 0
    assert "Created user" in result.stdout

def test_list_users():
    result = runner.invoke(cli, ["users", "list-users"])
    assert result.exit_code == 0
```

## Best Practices

1. **Always use async/await** - Match the rest of the codebase
2. **Initialize DB** - Call `init_db()` at start of async commands
3. **Handle errors gracefully** - Catch exceptions and exit with proper codes
4. **Provide helpful messages** - Use emoji and colors for clarity
5. **Add --help text** - Document all parameters
6. **Use confirmation prompts** - For destructive operations
7. **Show progress** - For long-running operations
8. **Validate inputs** - Check data before processing
9. **Use exit codes** - 0 for success, 1+ for errors
10. **Group related commands** - Keep CLI organized

## Environment Variables

CLI commands use the same configuration as the application:

```bash
# Set MongoDB URL
export MONGODB_URL=mongodb://localhost:27017/mydb

# Run command
python -m src.app.cli users list-users
```

## Need Help?

- Core CLI changes: `https://github.com/alltuner/scaffolding`
- Typer docs: `https://typer.tiangolo.com/`
- Rich docs: `https://rich.readthedocs.io/`
