# ABOUTME: Lazy re-export layer for the frontend package.
# ABOUTME: Defers app creation until explicitly requested to avoid circular imports.
from fastapi import Depends as Depends

from .routing import LocalizedRouter as LocalizedRouter, localized as localized


def __getattr__(name: str):
    if name == "app":
        from vibetuner.frontend.application import app

        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
