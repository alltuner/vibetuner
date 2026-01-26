# ABOUTME: Utility functions for vibetuner
# ABOUTME: Provides compute_auto_port for deterministic port calculation from paths
import hashlib
import os


def compute_auto_port(path: str | None = None) -> int:
    """Compute deterministic port from directory path.

    Args:
        path: Directory path to compute port for. Defaults to current directory.

    Returns:
        Port number in the range 8001-8999.
    """
    target_path = path or os.getcwd()
    hash_bytes = hashlib.sha256(target_path.encode()).digest()
    hash_int = int.from_bytes(hash_bytes[:4], "big")
    return 8001 + (hash_int % 999)
