# ABOUTME: Unit tests for port resolution in vibetuner.config
# ABOUTME: Tests _compute_auto_port, resolved_port, and resolved_worker_port
# ruff: noqa: S101

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError


class TestComputeAutoPort:
    """Test CoreConfiguration._compute_auto_port static method."""

    def test_returns_int_in_expected_range(self):
        """Test that auto port is in the range 10000-13999."""
        from vibetuner.config import CoreConfiguration

        port = CoreConfiguration._compute_auto_port("/some/path")
        assert isinstance(port, int)
        assert 10000 <= port <= 13999

    def test_deterministic_for_same_path(self):
        """Test that same path always returns same port."""
        from vibetuner.config import CoreConfiguration

        path = "/my/project/path"
        port1 = CoreConfiguration._compute_auto_port(path)
        port2 = CoreConfiguration._compute_auto_port(path)
        assert port1 == port2

    def test_different_paths_can_have_different_ports(self):
        """Test that different paths can produce different ports."""
        from vibetuner.config import CoreConfiguration

        port1 = CoreConfiguration._compute_auto_port("/path/a")
        port2 = CoreConfiguration._compute_auto_port("/path/b")
        assert port1 != port2

    def test_defaults_to_cwd_when_no_path_provided(self):
        """Test that None path uses current working directory."""
        from vibetuner.config import CoreConfiguration

        with patch.object(os, "getcwd", return_value="/test/cwd"):
            port_from_none = CoreConfiguration._compute_auto_port(None)
            port_from_explicit = CoreConfiguration._compute_auto_port("/test/cwd")
            assert port_from_none == port_from_explicit

    def test_defaults_to_cwd_when_called_without_args(self):
        """Test that calling without arguments uses current working directory."""
        from vibetuner.config import CoreConfiguration

        with patch.object(os, "getcwd", return_value="/test/cwd"):
            port_from_no_args = CoreConfiguration._compute_auto_port()
            port_from_explicit = CoreConfiguration._compute_auto_port("/test/cwd")
            assert port_from_no_args == port_from_explicit


class TestResolvedPort:
    """Test CoreConfiguration.resolved_port computed field."""

    def test_dev_port_overrides_auto_calc(self):
        """Test that DEV_PORT env var overrides auto-calculation."""
        from vibetuner.config import CoreConfiguration

        config = CoreConfiguration(
            dev_port=7500,
            environment="dev",
            _env_file=None,
        )
        assert config.resolved_port == 7500

    def test_prod_defaults_to_8000(self):
        """Test that production mode without DEV_PORT defaults to 8000."""
        from vibetuner.config import CoreConfiguration

        config = CoreConfiguration(
            environment="prod",
            _env_file=None,
        )
        assert config.resolved_port == 8000

    def test_dev_auto_calculates(self):
        """Test that dev mode without DEV_PORT auto-calculates."""
        from vibetuner.config import CoreConfiguration

        config = CoreConfiguration(
            environment="dev",
            _env_file=None,
        )
        assert 10000 <= config.resolved_port <= 13999


class TestResolvedWorkerPort:
    """Test CoreConfiguration.resolved_worker_port computed field."""

    def test_worker_port_overrides(self):
        """Test that WORKER_PORT env var overrides calculation."""
        from vibetuner.config import CoreConfiguration

        config = CoreConfiguration(
            dev_port=7500,
            worker_port=20000,
            environment="dev",
            _env_file=None,
        )
        assert config.resolved_worker_port == 20000

    def test_worker_port_derived_from_resolved_port(self):
        """Test that worker port = 10000 + resolved_port when no override."""
        from vibetuner.config import CoreConfiguration

        config = CoreConfiguration(
            dev_port=7500,
            environment="dev",
            _env_file=None,
        )
        assert config.resolved_worker_port == 17500

    def test_worker_port_prod_default(self):
        """Test that prod worker port = 10000 + 8000 = 18000."""
        from vibetuner.config import CoreConfiguration

        config = CoreConfiguration(
            environment="prod",
            _env_file=None,
        )
        assert config.resolved_worker_port == 18000


class TestPortValidation:
    """Test that dev_port and worker_port reject invalid port numbers."""

    @pytest.mark.parametrize("field", ["dev_port", "worker_port"])
    def test_rejects_privileged_port(self, field):
        """Ports below 1024 are rejected."""
        from vibetuner.config import CoreConfiguration

        with pytest.raises(ValidationError):
            CoreConfiguration(**{field: 80}, _env_file=None)

    @pytest.mark.parametrize("field", ["dev_port", "worker_port"])
    def test_rejects_port_above_max(self, field):
        """Ports above 65535 are rejected."""
        from vibetuner.config import CoreConfiguration

        with pytest.raises(ValidationError):
            CoreConfiguration(**{field: 99999}, _env_file=None)

    @pytest.mark.parametrize("field", ["dev_port", "worker_port"])
    def test_accepts_unprivileged_port(self, field):
        """Valid unprivileged ports (1024-65535) are accepted."""
        from vibetuner.config import CoreConfiguration

        config = CoreConfiguration(**{field: 8080}, _env_file=None)
        assert getattr(config, field) == 8080

    @pytest.mark.parametrize("field", ["dev_port", "worker_port"])
    def test_accepts_boundary_ports(self, field):
        """Boundary values 1024 and 65535 are accepted."""
        from vibetuner.config import CoreConfiguration

        low = CoreConfiguration(**{field: 1024}, _env_file=None)
        assert getattr(low, field) == 1024

        high = CoreConfiguration(**{field: 65535}, _env_file=None)
        assert getattr(high, field) == 65535
