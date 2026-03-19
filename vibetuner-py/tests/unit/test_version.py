# ABOUTME: Tests that vibetuner exposes a __version__ attribute.
# ABOUTME: Verifies the version matches the installed package metadata.
# ruff: noqa: S101
import vibetuner


class TestVersion:
    """Tests for vibetuner.__version__."""

    def test_version_is_exposed(self):
        """The vibetuner package exposes a __version__ attribute."""
        assert hasattr(vibetuner, "__version__")
        assert isinstance(vibetuner.__version__, str)

    def test_version_matches_metadata(self):
        """__version__ matches the installed package metadata."""
        from importlib.metadata import version

        assert vibetuner.__version__ == version("vibetuner")

    def test_version_in_all(self):
        """__version__ is listed in __all__."""
        assert "__version__" in vibetuner.__all__
