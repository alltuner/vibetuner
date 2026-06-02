# ABOUTME: Enables `python -m vibetuner`, sharing the console script entry point.
# ABOUTME: Routes through main() so the worker-health fast path applies here too.
from .cli import main


main()
