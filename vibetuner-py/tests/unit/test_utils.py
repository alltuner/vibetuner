# ABOUTME: Unit tests for vibetuner.utils module
# ABOUTME: Tests auto-port computation utility function
# ruff: noqa: S101

import os
from unittest.mock import patch


class TestComputeAutoPort:
    """Test compute_auto_port utility function."""

    def test_returns_int_in_expected_range(self):
        """Test that auto port is in the range 8001-8999."""
        from vibetuner.utils import compute_auto_port

        port = compute_auto_port("/some/path")
        assert isinstance(port, int)
        assert 8001 <= port <= 8999

    def test_deterministic_for_same_path(self):
        """Test that same path always returns same port."""
        from vibetuner.utils import compute_auto_port

        path = "/my/project/path"
        port1 = compute_auto_port(path)
        port2 = compute_auto_port(path)
        assert port1 == port2

    def test_different_paths_can_have_different_ports(self):
        """Test that different paths can produce different ports."""
        from vibetuner.utils import compute_auto_port

        port1 = compute_auto_port("/path/a")
        port2 = compute_auto_port("/path/b")
        # Not guaranteed to be different, but these specific paths differ
        assert port1 != port2

    def test_defaults_to_cwd_when_no_path_provided(self):
        """Test that None path uses current working directory."""
        from vibetuner.utils import compute_auto_port

        with patch.object(os, "getcwd", return_value="/test/cwd"):
            port_from_none = compute_auto_port(None)
            port_from_explicit = compute_auto_port("/test/cwd")
            assert port_from_none == port_from_explicit

    def test_defaults_to_cwd_when_called_without_args(self):
        """Test that calling without arguments uses current working directory."""
        from vibetuner.utils import compute_auto_port

        with patch.object(os, "getcwd", return_value="/test/cwd"):
            port_from_no_args = compute_auto_port()
            port_from_explicit = compute_auto_port("/test/cwd")
            assert port_from_no_args == port_from_explicit
