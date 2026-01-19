# ABOUTME: Tests for the Context model.
# ABOUTME: Validates locale_names property behavior for language display names.
# ruff: noqa: S101
"""Tests for the Context model."""


def test_locale_names_returns_sorted_dict():
    """locale_names returns language codes mapped to native display names, sorted alphabetically."""
    from vibetuner.context import Context

    ctx = Context()
    ctx.__dict__["supported_languages"] = {"en", "es", "ca"}

    names = ctx.locale_names

    assert isinstance(names, dict)
    assert "en" in names
    assert "es" in names
    assert "ca" in names
    # Values should be native display names
    assert names["en"] == "English"
    assert names["es"] == "Español"
    assert names["ca"] == "Català"
    # Sorted alphabetically by display name: Català, English, Español
    assert list(names.keys()) == ["ca", "en", "es"]


def test_locale_names_handles_single_language():
    """locale_names works with a single language."""
    from vibetuner.context import Context

    ctx = Context()
    ctx.__dict__["supported_languages"] = {"en"}

    names = ctx.locale_names

    assert names == {"en": "English"}


def test_locale_names_is_cached():
    """locale_names result is cached after first access."""
    from vibetuner.context import Context

    ctx = Context()
    ctx.__dict__["supported_languages"] = {"en", "es"}

    # Access twice
    names1 = ctx.locale_names
    names2 = ctx.locale_names

    # Should be the same object (cached)
    assert names1 is names2
