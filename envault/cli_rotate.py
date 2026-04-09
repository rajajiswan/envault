"""CLI command for rotating a vault passphrase."""

from __future__ import annotations

import click

from envault.rotate import rotate_passphrase, RotationError


@click.command("rotate")
@click.argument("vault_name")
@click.option(
    "--old-passphrase",
    prompt="Current passphrase",
    hide_input=True,
    help="Passphrase currently protecting the vault.",
)
@click.option(
    "--new-passphrase",
    prompt="New passphrase",
    hide_input=True,
    confirmation_prompt="Confirm new passphrase",
    help="Replacement passphrase for the vault.",
)
def rotate_cmd(vault_name: str, old_passphrase: str, new_passphrase: str) -> None:
    """Rotate the passphrase for VAULT_NAME.

    The vault is decrypted with the current passphrase and immediately
    re-encrypted with the new one.  The original file is replaced in place.
    """
    if old_passphrase == new_passphrase:
        click.echo("New passphrase must differ from the current passphrase.", err=True)
        raise SystemExit(1)

    try:
        rotate_passphrase(vault_name, old_passphrase, new_passphrase)
    except RotationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"Passphrase for vault '{vault_name}' rotated successfully.")
