# ABOUTME: CLI command to forward Claude Code hook events to local dev server
# ABOUTME: Used by Claude hooks to notify the vibetuner app of events
import os
import sys
from pathlib import Path

import httpx
import typer
from rich.console import Console


console = Console()

notify_app = typer.Typer(
    help="Claude Code notification commands", no_args_is_help=False
)

DEFAULT_PORT = 8000
PORT_FILE = Path(".vibetuner-port")


def _discover_port() -> int:
    """Discover the local dev server port."""
    if env_port := os.environ.get("VIBETUNER_PORT"):
        return int(env_port)

    if PORT_FILE.exists():
        return int(PORT_FILE.read_text().strip())

    return DEFAULT_PORT


@notify_app.callback(invoke_without_command=True)
def notify(
    port: int | None = typer.Option(None, "--port", "-p", help="Override port"),
) -> None:
    """Receive Claude Code hook events and forward to local dev server.

    Reads JSON payload from stdin and POSTs to /api/claude/webhook.
    Fails silently if server isn't running (non-blocking for Claude).
    """
    payload = sys.stdin.read()

    if not payload.strip():
        return

    target_port = port or _discover_port()
    url = f"http://localhost:{target_port}/api/claude/webhook"

    try:
        httpx.post(
            url,
            content=payload,
            headers={"Content-Type": "application/json"},
            timeout=2.0,
        )
    except Exception:  # noqa: S110 - intentionally silent to avoid blocking Claude
        pass
