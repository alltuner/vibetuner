# ABOUTME: CLI commands for debug access to deployed vibetuner applications.
# ABOUTME: Generates HMAC-signed magic links that grant short-lived debug access.
from typing import Annotated

import typer


debug_app = typer.Typer(help="Debug access for deployed applications", no_args_is_help=True)


@debug_app.command()
def open(
    url: Annotated[str, typer.Argument(help="Base URL of the deployed application")],
    secret: Annotated[
        str | None,
        typer.Option(
            "--secret",
            "-s",
            help="Signing secret (must match SESSION_KEY on server). "
            "Falls back to local project config when omitted.",
        ),
    ] = None,
) -> None:
    """Generate a short-lived HMAC-signed link and open the debug dashboard."""
    from rich.console import Console

    from vibetuner.debug_signing import generate_debug_url

    console = Console()

    if secret is None:
        try:
            from vibetuner.config import settings

            secret = settings.session_key.get_secret_value()
        except Exception:
            console.print(
                "[red]Could not read SESSION_KEY from project config. "
                "Use --secret to provide it explicitly.[/red]"
            )
            raise typer.Exit(code=1) from None

    debug_url = generate_debug_url(url, secret)
    console.print("[dim]Opening debug link (expires in 5 minutes)...[/dim]")
    typer.launch(debug_url)
