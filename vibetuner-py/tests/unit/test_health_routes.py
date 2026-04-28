# ABOUTME: Regression tests for /health/ready service detection logic.
# ABOUTME: Pins the email-provider check after the settings.mailjet_api_key bug.
# ruff: noqa: S101

from unittest.mock import MagicMock, patch

import pytest


def _patch_mail_settings(**kwargs):
    """Swap settings.mail with a MagicMock carrying the given attributes."""
    fake = MagicMock()
    fake.provider = kwargs.get("provider")
    for attr in (
        "resend_api_key",
        "mailjet_api_key",
        "mailjet_api_secret",
        "cloudflare_api_token",
        "cloudflare_account_id",
    ):
        fake.__setattr__(attr, kwargs.get(attr))
    return patch("vibetuner.services.email.service.settings.mail", fake)


def _secret(value: str):
    sec = MagicMock()
    sec.get_secret_value.return_value = value
    sec.__bool__ = lambda self: True
    return sec


def _patch_top_level_settings(**kwargs):
    """Patch top-level settings attrs consulted by _check_all_services."""
    return patch.multiple(
        "vibetuner.frontend.routes.health.settings",
        mongodb_url=kwargs.get("mongodb_url"),
        redis_url=kwargs.get("redis_url"),
        r2_bucket_endpoint_url=kwargs.get("r2_bucket_endpoint_url"),
    )


@pytest.mark.asyncio
async def test_check_all_services_does_not_crash_with_no_email_configured():
    """Regression: previously settings.mailjet_api_key raised AttributeError."""
    from vibetuner.frontend.routes.health import _check_all_services

    with _patch_top_level_settings(), _patch_mail_settings():
        services = await _check_all_services()

    assert "email" not in services


@pytest.mark.asyncio
async def test_check_all_services_includes_email_when_resend_configured():
    from vibetuner.frontend.routes.health import _check_all_services

    with (
        _patch_top_level_settings(),
        _patch_mail_settings(resend_api_key=_secret("re_xxx")),
    ):
        services = await _check_all_services()

    assert services["email"] == {"status": "configured", "provider": "resend"}


@pytest.mark.asyncio
async def test_check_all_services_includes_email_when_mailjet_configured():
    from vibetuner.frontend.routes.health import _check_all_services

    with (
        _patch_top_level_settings(),
        _patch_mail_settings(
            mailjet_api_key=_secret("k"),
            mailjet_api_secret=_secret("s"),
        ),
    ):
        services = await _check_all_services()

    assert services["email"] == {"status": "configured", "provider": "mailjet"}


@pytest.mark.asyncio
async def test_check_all_services_includes_email_when_cloudflare_configured():
    from vibetuner.frontend.routes.health import _check_all_services

    with (
        _patch_top_level_settings(),
        _patch_mail_settings(
            cloudflare_api_token=_secret("cf-token"),
            cloudflare_account_id="acct-xyz",
        ),
    ):
        services = await _check_all_services()

    assert services["email"] == {"status": "configured", "provider": "cloudflare"}


@pytest.mark.asyncio
async def test_check_all_services_skips_email_when_provider_set_without_creds():
    """Misconfigured MAIL_PROVIDER (no creds) → email row absent, no crash."""
    from vibetuner.frontend.routes.health import _check_all_services

    with (
        _patch_top_level_settings(),
        _patch_mail_settings(provider="cloudflare"),
    ):
        services = await _check_all_services()

    assert "email" not in services
