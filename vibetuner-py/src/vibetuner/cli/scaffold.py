# ABOUTME: Scaffolding commands for creating new projects from the vibetuner template
# ABOUTME: Uses Copier to generate FastAPI+MongoDB+HTMX projects with interactive prompts
from pathlib import Path
from typing import Annotated

import copier
import typer
from rich.console import Console


console = Console()

scaffold_app = typer.Typer(
    help="Create new projects from the vibetuner template", no_args_is_help=True
)


def get_template_path() -> Path:
    """Get the path to the vibetuner template directory."""
    # This file is at: vibetuner-py/src/vibetuner/cli/scaffold.py
    # Template is at: ./ (root of repo)
    current_file = Path(__file__).resolve()
    # Go up: scaffold.py -> cli -> vibetuner -> src -> vibetuner-py -> repo_root
    template_path = current_file.parent.parent.parent.parent.parent
    return template_path


@scaffold_app.command(name="new")
def new(
    destination: Annotated[
        Path,
        typer.Argument(
            help="Destination directory for the new project",
            exists=False,
        ),
    ],
    template: Annotated[
        str | None,
        typer.Option(
            "--template",
            "-t",
            help="Template source (git URL, local path, or github:user/repo). Defaults to local vibetuner template.",
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
) -> None:
    """Create a new project from the vibetuner template.

    Examples:

        # Interactive mode (prompts for all values)
        vibetuner scaffold new my-project

        # Use defaults for all prompts
        vibetuner scaffold new my-project --defaults

        # Override specific values
        vibetuner scaffold new my-project --data project_name="My App" --data python_version="3.13"

        # Use a different template source
        vibetuner scaffold new my-project --template gh:alltuner/vibetuner
        vibetuner scaffold new my-project --template /path/to/template
    """
    # Determine template source
    if template is None:
        template_src = get_template_path()
        console.print(f"[dim]Using local template: {template_src}[/dim]")
    else:
        template_src = template
        console.print(f"[dim]Using template: {template_src}[/dim]")

    # Parse data overrides
    data_dict = {}
    if data:
        for item in data:
            if "=" not in item:
                console.print(f"[red]Error: Invalid data format '{item}'. Expected key=value[/red]")
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
        )

        console.print(f"\n[green]✓ Project created successfully![/green]")
        console.print(f"\nNext steps:")
        console.print(f"  cd {destination}")
        console.print(f"  just dev")

    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        raise typer.Exit(code=1)


@scaffold_app.command(name="update")
def update(
    path: Annotated[
        Path,
        typer.Argument(
            help="Path to the project to update",
        ),
    ] = Path.cwd(),
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
    if not path.exists():
        console.print(f"[red]Error: Directory does not exist: {path}[/red]")
        raise typer.Exit(code=1)

    # Check if it's a copier project
    answers_file = path / ".copier-answers.yml"
    if not answers_file.exists():
        console.print(
            f"[red]Error: Not a copier project (missing .copier-answers.yml)[/red]"
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

        console.print(f"\n[green]✓ Project updated successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error updating project: {e}[/red]")
        raise typer.Exit(code=1)
