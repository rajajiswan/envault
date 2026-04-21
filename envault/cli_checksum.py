"""CLI commands for vault checksum management."""

import click

from envault.checksum import (
    ChecksumError,
    clear_checksum,
    load_checksum,
    save_checksum,
    verify_checksum,
)


@click.group("checksum")
def checksum_cmd() -> None:
    """Manage vault content checksums."""


@checksum_cmd.command("record")
@click.argument("vault_name")
@click.password_option("--passphrase", prompt="Passphrase", confirmation_prompt=False)
def record_cmd(vault_name: str, passphrase: str) -> None:
    """Compute and save a checksum for VAULT_NAME."""
    try:
        digest = save_checksum(vault_name, passphrase)
        click.echo(f"Checksum recorded: {digest}")
    except ChecksumError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@checksum_cmd.command("verify")
@click.argument("vault_name")
@click.password_option("--passphrase", prompt="Passphrase", confirmation_prompt=False)
def verify_cmd(vault_name: str, passphrase: str) -> None:
    """Verify VAULT_NAME contents against its stored checksum."""
    try:
        ok = verify_checksum(vault_name, passphrase)
    except ChecksumError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if ok:
        click.echo("Checksum OK — vault contents are unchanged.")
    else:
        click.echo("Checksum MISMATCH — vault contents have changed!", err=True)
        raise SystemExit(1)


@checksum_cmd.command("show")
@click.argument("vault_name")
def show_cmd(vault_name: str) -> None:
    """Display the stored checksum for VAULT_NAME."""
    digest = load_checksum(vault_name)
    if digest is None:
        click.echo(f"No checksum recorded for '{vault_name}'.")
    else:
        click.echo(digest)


@checksum_cmd.command("clear")
@click.argument("vault_name")
def clear_cmd(vault_name: str) -> None:
    """Remove the stored checksum for VAULT_NAME."""
    clear_checksum(vault_name)
    click.echo(f"Checksum cleared for '{vault_name}'.")
