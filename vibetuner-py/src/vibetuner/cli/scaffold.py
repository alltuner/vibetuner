# ABOUTME: Scaffolding commands for creating new projects from the vibetuner template
# ABOUTME: Uses Copier to generate FastAPI+MongoDB+HTMX projects with interactive prompts
import tomllib
from pathlib import Path
from typing import Annotated

import copier
import typer
from rich.console import Console


console = Console()


def _get_git_config(key: str, cwd: Path) -> str | None:
    """Get a git config value, returning None if not found.

    Args:
        key: Config key in "section.option" format (e.g., "user.name", "user.email")
        cwd: Directory to search for git repository from
    """
    try:
        import git
    except ImportError:
        return None
    try:
        repo = git.Repo(cwd, search_parent_directories=True)
        reader = repo.config_reader()
        section, option = key.split(".", 1)
        return reader.get_value(section, option)
    except (git.InvalidGitRepositoryError, git.GitError, KeyError, ValueError):
        return None


def _infer_from_pyproject(path: Path) -> dict[str, str]:
    """Infer template variables from pyproject.toml."""
    data: dict[str, str] = {}
    pyproject_path = path / "pyproject.toml"

    if not pyproject_path.exists():
        return data

    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)

    project = pyproject.get("project", {})

    if name := project.get("name"):
        data["project_name"] = name
        data["project_slug"] = name.lower().replace("_", "-").replace(" ", "-")

    if description := project.get("description"):
        data["project_description"] = description

    authors = project.get("authors", [])
    if authors and isinstance(authors, list) and isinstance(authors[0], dict):
        first_author = authors[0]
        if author_name := first_author.get("name"):
            data["author_name"] = author_name
        if author_email := first_author.get("email"):
            data["author_email"] = author_email

    return data


def _infer_python_version(path: Path) -> str | None:
    """Infer Python version from .python-version file."""
    python_version_path = path / ".python-version"
    if not python_version_path.exists():
        return None

    version_str = python_version_path.read_text().strip()
    parts = version_str.split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return None


def _infer_project_data(path: Path) -> dict[str, str]:
    """Infer template variables from existing project files.

    Reads project metadata from pyproject.toml and other files to pre-fill
    Copier template variables when adopting an existing project.
    """
    data = _infer_from_pyproject(path)

    if "author_name" not in data:
        if git_name := _get_git_config("user.name", path):
            data["author_name"] = git_name

    if "author_email" not in data:
        if git_email := _get_git_config("user.email", path):
            data["author_email"] = git_email

    if python_version := _infer_python_version(path):
        data["python_version"] = python_version

    return data


def _has_vibetuner_dependency(path: Path) -> bool:
    """Check if vibetuner is listed as a dependency in pyproject.toml."""
    pyproject_path = path / "pyproject.toml"
    if not pyproject_path.exists():
        return False

    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)

    project = pyproject.get("project", {})
    dependencies = project.get("dependencies", [])

    return any(
        isinstance(dep, str) and dep.startswith("vibetuner") for dep in dependencies
    )


def _validate_adopt_path(path: Path) -> None:
    """Validate path for adopt command, raising typer.Exit on errors."""
    if not path.exists():
        console.print(f"[red]Error: Directory does not exist: {path}[/red]")
        raise typer.Exit(code=1)

    if not path.is_dir():
        console.print(f"[red]Error: Path is not a directory: {path}[/red]")
        raise typer.Exit(code=1)

    pyproject_path = path / "pyproject.toml"
    if not pyproject_path.exists():
        console.print(f"[red]Error: pyproject.toml not found in {path}[/red]")
        console.print(
            "[yellow]The adopt command requires an existing Python project "
            "with pyproject.toml[/yellow]"
        )
        raise typer.Exit(code=1)

    if not _has_vibetuner_dependency(path):
        console.print(
            "[red]Error: vibetuner is not listed as a dependency in pyproject.toml[/red]"
        )
        console.print(
            "[yellow]Add vibetuner to your dependencies first: uv add vibetuner[/yellow]"
        )
        raise typer.Exit(code=1)

    answers_file = path / ".copier-answers.yml"
    if answers_file.exists():
        console.print(
            "[red]Error: Project is already scaffolded (.copier-answers.yml exists)[/red]"
        )
        console.print(
            "[yellow]Use 'vibetuner scaffold update' to update an existing "
            "scaffolded project[/yellow]"
        )
        raise typer.Exit(code=1)


def _parse_data_overrides(data: list[str] | None) -> dict[str, str]:
    """Parse --data key=value arguments into a dictionary."""
    if not data:
        return {}

    result: dict[str, str] = {}
    for item in data:
        if "=" not in item:
            console.print(
                f"[red]Error: Invalid data format '{item}'. Expected key=value[/red]"
            )
            raise typer.Exit(code=1)
        key, value = item.split("=", 1)
        result[key] = value
    return result


scaffold_app = typer.Typer(
    help="Create new projects from the vibetuner template", no_args_is_help=True
)


@scaffold_app.command(name="new")
def new(
    destination: Annotated[
        Path,
        typer.Argument(
            help="Destination directory for the new project",
            exists=False,
        ),
    ],
    defaults: Annotated[
        bool,
        typer.Option(
            "--defaults",
            "-d",
            help="Use default values for all prompts (non-interactive mode)",
        ),
    ] = False,
    data: Annotated[
        list[str] | None,
        typer.Option(
            "--data",
            help="Override template variables in key=value format (can be used multiple times)",
        ),
    ] = None,
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch",
            "-b",
            help="Use specific branch/tag from the vibetuner template repository",
        ),
    ] = None,
) -> None:
    """Create a new project from the vibetuner template.

    Examples:

        # Interactive mode (prompts for all values)
        vibetuner scaffold new my-project

        # Use defaults for all prompts
        vibetuner scaffold new my-project --defaults

        # Override specific values
        vibetuner scaffold new my-project --data project_name="My App" --data python_version="3.13"

        # Use specific branch for testing
        vibetuner scaffold new my-project --branch fix/scaffold-command
    """
    # Use the official vibetuner template from GitHub
    template_src = "gh:alltuner/vibetuner"
    vcs_ref = branch or "main"  # Use specified branch or default to main

    if branch:
        console.print(
            f"[dim]Using vibetuner template from GitHub ({branch} branch)[/dim]"
        )
    else:
        console.print("[dim]Using vibetuner template from GitHub (main branch)[/dim]")

    # Parse data overrides
    data_dict = {}
    if data:
        for item in data:
            if "=" not in item:
                console.print(
                    f"[red]Error: Invalid data format '{item}'. Expected key=value[/red]"
                )
                raise typer.Exit(code=1)
            key, value = item.split("=", 1)
            data_dict[key] = value

    # When using defaults, provide sensible default values for required fields
    if defaults:
        default_values = {
            "company_name": "Acme Corp",
            "author_name": "Developer",
            "author_email": "dev@example.com",
            "supported_languages": [],
        }
        # Merge: user overrides take precedence over defaults
        data_dict = {**default_values, **data_dict}

    # Run copier
    try:
        console.print(f"\n[green]Creating new project in: {destination}[/green]\n")

        copier.run_copy(
            src_path=str(template_src),
            dst_path=destination,
            data=data_dict if data_dict else None,
            defaults=defaults,
            quiet=defaults,  # Suppress prompts when using defaults
            unsafe=True,  # Allow running post-generation tasks
            vcs_ref=vcs_ref,  # Use the specified branch or default to main
        )

        console.print("\n[green]✓ Project created successfully![/green]")
        console.print("\nNext steps:")
        console.print(f"  cd {destination}")
        console.print("  just dev")

    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        raise typer.Exit(code=1) from None


@scaffold_app.command(name="update")
def update(
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to the project to update",
        ),
    ] = None,
    skip_answered: Annotated[
        bool,
        typer.Option(
            "--skip-answered",
            "-s",
            help="Skip questions that have already been answered",
        ),
    ] = True,
) -> None:
    """Update an existing project to the latest template version.

    This will update the project's files to match the latest template version,
    while preserving your answers to the original questions.

    Examples:

        # Update current directory
        vibetuner scaffold update

        # Update specific directory
        vibetuner scaffold update /path/to/project

        # Re-prompt for all questions
        vibetuner scaffold update --no-skip-answered
    """
    if path is None:
        path = Path.cwd()

    if not path.exists():
        console.print(f"[red]Error: Directory does not exist: {path}[/red]")
        raise typer.Exit(code=1)

    # Check if it's a copier project
    answers_file = path / ".copier-answers.yml"
    if not answers_file.exists():
        console.print(
            "[red]Error: Not a copier project (missing .copier-answers.yml)[/red]"
        )
        console.print(f"[yellow]Directory: {path}[/yellow]")
        raise typer.Exit(code=1)

    try:
        console.print(f"\n[green]Updating project: {path}[/green]\n")

        copier.run_update(
            dst_path=path,
            skip_answered=skip_answered,
            unsafe=True,  # Allow running post-generation tasks
        )

        console.print("\n[green]✓ Project updated successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error updating project: {e}[/red]")
        raise typer.Exit(code=1) from None


@scaffold_app.command(name="copy-core-templates", hidden=True)
def copy_core_templates() -> None:
    """Deprecated: This command is a no-op kept for backwards compatibility."""
    console.print("[dim]This command is deprecated and does nothing.[/dim]")


@scaffold_app.command(name="adopt")
def adopt(
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to the existing project to adopt (defaults to current directory)",
        ),
    ] = None,
    defaults: Annotated[
        bool,
        typer.Option(
            "--defaults",
            "-d",
            help="Use default values for all prompts (non-interactive mode)",
        ),
    ] = False,
    data: Annotated[
        list[str] | None,
        typer.Option(
            "--data",
            help="Override template variables in key=value format (can be used multiple times)",
        ),
    ] = None,
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch",
            "-b",
            help="Use specific branch/tag from the vibetuner template repository",
        ),
    ] = None,
) -> None:
    """Adopt vibetuner scaffolding for an existing project.

    This command allows projects that already have vibetuner installed as a
    dependency to adopt the full scaffolding infrastructure, enabling future
    `scaffold update` commands.

    The command will:
    1. Infer template variables from existing project files (pyproject.toml, etc.)
    2. Apply the vibetuner template to the existing directory
    3. Prompt for conflict resolution on existing files

    Examples:

        # Adopt scaffolding in current directory
        vibetuner scaffold adopt

        # Adopt scaffolding in specific directory
        vibetuner scaffold adopt /path/to/project

        # Use specific branch for testing
        vibetuner scaffold adopt --branch fix/scaffold-command

        # Override inferred values
        vibetuner scaffold adopt --data company_name="My Company"
    """
    if path is None:
        path = Path.cwd()

    _validate_adopt_path(path)

    template_src = "gh:alltuner/vibetuner"
    vcs_ref = branch or "main"

    if branch:
        console.print(
            f"[dim]Using vibetuner template from GitHub ({branch} branch)[/dim]"
        )
    else:
        console.print("[dim]Using vibetuner template from GitHub (main branch)[/dim]")

    inferred_data = _infer_project_data(path)
    if inferred_data:
        console.print("\n[dim]Inferred values from existing project:[/dim]")
        for key, value in inferred_data.items():
            console.print(f"  [dim]{key}: {value}[/dim]")

    user_overrides = _parse_data_overrides(data)
    default_values = {"company_name": "Acme Corp", "supported_languages": []}

    # Merge: defaults -> inferred -> user overrides (later takes precedence)
    data_dict: dict = {**default_values, **inferred_data, **user_overrides}

    # Run copier
    try:
        console.print(f"\n[green]Adopting scaffolding in: {path}[/green]\n")
        console.print(
            "[yellow]Copier will prompt for conflict resolution on existing files.[/yellow]\n"
        )

        copier.run_copy(
            src_path=str(template_src),
            dst_path=path,
            data=data_dict if data_dict else None,
            defaults=defaults,
            quiet=defaults,
            unsafe=True,
            vcs_ref=vcs_ref,
        )

        console.print("\n[green]✓ Scaffolding adopted successfully![/green]")
        console.print("\nNext steps:")
        console.print("  1. Review changes: git diff")
        console.print("  2. Resolve any conflicts in pyproject.toml")
        console.print("  3. Sync dependencies: uv sync")
        console.print("  4. Start development: just dev")
        console.print(
            "\nYou can now use 'vibetuner scaffold update' to update to future template versions."
        )

    except Exception as e:
        console.print(f"[red]Error adopting scaffolding: {e}[/red]")
        raise typer.Exit(code=1) from None
