# ABOUTME: Background task modules for the application.
# ABOUTME: Tasks are registered via decorators when imported by the worker.

# NOTE: Task modules should NOT be imported here to avoid circular imports
# with vibetuner.tasks.worker. Import them inside lifespan.py within the
# lifespan context instead.
#
# Why: The worker needs to import lifespan.py before it's fully initialized.
# If this __init__.py imports task modules that depend on the worker, you'll
# get: "cannot import name 'worker' from partially initialized module".
#
# Correct pattern (in lifespan.py):
#   async with base_lifespan() as worker_ctx:
#       from . import emails
#       from . import reports
#       yield Context(**worker_ctx.model_dump())

__all__ = [
    # Do NOT add task module names here
]
