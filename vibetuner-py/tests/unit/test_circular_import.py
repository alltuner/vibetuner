# ABOUTME: Tests that render_template is importable without triggering the frontend app factory.
# ABOUTME: Regression tests for circular import issue #930.
# ruff: noqa: S101, S603, S607
import subprocess
import sys
import textwrap


class TestCircularImportPrevention:
    """Verify that render_template can be imported without triggering load_app_config().

    When user route files import render_template at module level, it must not trigger
    load_app_config() which would try to load tune.py and cause a circular import.

    The fix: render_template lives in vibetuner.rendering (outside vibetuner.frontend),
    so importing it never triggers the frontend app factory.

    See: https://github.com/alltuner/vibetuner/issues/930
    """

    def test_render_template_importable_from_rendering_module(self):
        """vibetuner.rendering must not trigger load_app_config()."""
        code = textwrap.dedent("""\
            import unittest.mock as mock
            import vibetuner.loader

            mock.patch.object(
                vibetuner.loader,
                "load_app_config",
                side_effect=RuntimeError("load_app_config called during import"),
            ).start()

            from vibetuner.rendering import render_template  # noqa: F401

            print("OK")
        """)

        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert "OK" in result.stdout, (
            f"Importing from vibetuner.rendering triggered load_app_config():\n"
            f"stderr: {result.stderr}"
        )

    def test_render_template_importable_from_vibetuner_top_level(self):
        """from vibetuner import render_template must not trigger load_app_config()."""
        code = textwrap.dedent("""\
            import unittest.mock as mock
            import vibetuner.loader

            mock.patch.object(
                vibetuner.loader,
                "load_app_config",
                side_effect=RuntimeError("load_app_config called during import"),
            ).start()

            from vibetuner import render_template  # noqa: F401

            print("OK")
        """)

        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert "OK" in result.stdout, (
            f"Importing from vibetuner triggered load_app_config():\n"
            f"stderr: {result.stderr}"
        )

    def test_render_template_string_importable_from_vibetuner(self):
        """render_template_string must also be importable from vibetuner."""
        code = textwrap.dedent("""\
            import unittest.mock as mock
            import vibetuner.loader

            mock.patch.object(
                vibetuner.loader,
                "load_app_config",
                side_effect=RuntimeError("load_app_config called during import"),
            ).start()

            from vibetuner import render_template_string  # noqa: F401

            print("OK")
        """)

        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert "OK" in result.stdout, (
            f"Importing render_template_string triggered load_app_config():\n"
            f"stderr: {result.stderr}"
        )
