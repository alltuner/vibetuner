# ABOUTME: CLI console entry point with a fast path for container healthchecks.
# ABOUTME: Builds the full Typer app lazily so probes skip the heavy bootstrap.
import sys


def main() -> None:
    """Console entry point.

    Container healthchecks must finish well under their timeout, but building
    the full Typer app imports every sub-command and the user's tune.py (config,
    BlobService, rate limiter), which can take several seconds. Dispatch the
    healthcheck directly before any of that is imported; everything else builds
    the full app as usual.
    """
    if sys.argv[1:2] == ["worker-health"]:
        from vibetuner.cli.health import run

        run()
        return

    from vibetuner.cli.root import app

    app()


def __getattr__(name: str):
    if name in ("app", "AsyncTyper"):
        import vibetuner.cli.root as root

        return getattr(root, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
