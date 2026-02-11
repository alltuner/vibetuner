# ABOUTME: Utility functions for vibetuner
# ABOUTME: Provides compute_auto_port for deterministic port calculation from paths
import hashlib
import os


def compute_auto_port(
    path: str | None = None, port_min: int = 8001, port_max: int = 8999
) -> int:
    """Compute deterministic port from directory path.

    Args:
        path: Directory path to compute port for. Defaults to current directory.
        port_min: Minimum port number (inclusive).
        port_max: Maximum port number (inclusive).

    Returns:
        Port number in the range port_min to port_max.
    """
    target_path = path or os.getcwd()
    hash_bytes = hashlib.sha256(target_path.encode()).digest()
    hash_int = int.from_bytes(hash_bytes[:4], "big")
    port_range = port_max - port_min + 1
    return port_min + (hash_int % port_range)
