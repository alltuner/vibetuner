# ABOUTME: CLI commands for managing field encryption keys.
# ABOUTME: Provides set-key and rotate-key for Fernet encryption of secrets at rest.
import secrets
from pathlib import Path
from typing import Annotated

import asyncer
import typer


crypto_app = typer.Typer(
    help="Manage encryption keys for secrets at rest", no_args_is_help=True
)


async def _set_key_impl(passphrase: str, env_file: Path) -> None:
    from pydantic import ValidationError

    from vibetuner.config import settings
    from vibetuner.crypto import encrypt_value, is_encrypted, write_env_var
    from vibetuner.models.oauth_app import OAuthProviderAppModel
    from vibetuner.mongo import init_mongodb

    await init_mongodb()

    # Set the key in memory so decrypt/encrypt hooks
    # can use it when Beanie validates documents during load and save.
    settings.field_encryption_key = passphrase

    try:
        apps = await OAuthProviderAppModel.find_all().to_list()
    except (ValidationError, ValueError):
        typer.echo(
            "Error: The database contains fields encrypted with a different key.\n"
            "Use 'vibetuner crypto set-key --key <existing-key>' to provide the "
            "correct key, or 'vibetuner crypto rotate-key' if you already have "
            "a working key configured.",
            err=True,
        )
        raise typer.Exit(1) from None

    encrypted_count = 0
    for app in apps:
        if not is_encrypted(app.client_secret):
            app.client_secret = encrypt_value(app.client_secret, passphrase)
            await app.save()
            encrypted_count += 1

    write_env_var(env_file, "FIELD_ENCRYPTION_KEY", passphrase)

    typer.echo(f"Encryption key written to {env_file}")
    typer.echo(f"Encrypted {encrypted_count} secret(s) across {len(apps)} app(s).")


async def _rotate_key_impl(
    old_passphrase: str, new_passphrase: str, env_file: Path
) -> None:
    from vibetuner.crypto import (
        decrypt_value,
        encrypt_value,
        is_encrypted,
        write_env_var,
    )
    from vibetuner.models.oauth_app import OAuthProviderAppModel
    from vibetuner.mongo import init_mongodb

    await init_mongodb()
    apps = await OAuthProviderAppModel.find_all().to_list()

    rotated_count = 0
    for app in apps:
        if is_encrypted(app.client_secret):
            plaintext = decrypt_value(app.client_secret, old_passphrase)
            app.client_secret = encrypt_value(plaintext, new_passphrase)
            await app.save()
            rotated_count += 1

    write_env_var(env_file, "FIELD_ENCRYPTION_KEY", new_passphrase)

    typer.echo(f"New encryption key written to {env_file}")
    typer.echo(f"Rotated {rotated_count} secret(s) across {len(apps)} app(s).")


@crypto_app.command("set-key")
def set_key(
    key: Annotated[
        str | None,
        typer.Option(
            "--key",
            "-k",
            help="Encryption passphrase. Generated automatically if omitted.",
        ),
    ] = None,
    env_file: Annotated[
        Path,
        typer.Option(
            "--env-file",
            "-e",
            help="Path to .env file to write the key to.",
        ),
    ] = Path(".env"),
) -> None:
    """Set the encryption key and encrypt all existing plaintext secrets."""
    from vibetuner.config import settings

    if settings.field_encryption_key is not None:
        typer.echo(
            "Error: An encryption key is already configured. "
            "Use 'vibetuner crypto rotate-key' to change it.",
            err=True,
        )
        raise typer.Exit(1)

    passphrase = key or secrets.token_urlsafe(32)
    asyncer.runnify(_set_key_impl)(passphrase, env_file)


@crypto_app.command("rotate-key")
def rotate_key(
    new_key: Annotated[
        str | None,
        typer.Option(
            "--new-key",
            "-k",
            help="New encryption passphrase. Generated automatically if omitted.",
        ),
    ] = None,
    env_file: Annotated[
        Path,
        typer.Option(
            "--env-file",
            "-e",
            help="Path to .env file to update with the new key.",
        ),
    ] = Path(".env"),
) -> None:
    """Rotate the encryption key: re-encrypt all secrets with a new key."""
    from vibetuner.config import settings

    old_passphrase = settings.field_encryption_key
    if old_passphrase is None:
        typer.echo(
            "Error: No encryption key is configured. "
            "Use 'vibetuner crypto set-key' first.",
            err=True,
        )
        raise typer.Exit(1)

    new_passphrase = new_key or secrets.token_urlsafe(32)
    asyncer.runnify(_rotate_key_impl)(old_passphrase, new_passphrase, env_file)
