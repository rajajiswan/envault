"""CLI commands for vault compression and decompression."""

from __future__ import annotations

import click

from envault.compress import CompressError, compress_vault, decompress_vault


@click.group("compress")
def compress_cmd() -> None:
    """Compress and decompress vaults."""


@compress_cmd.command("pack")
@click.argument("name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option("--dest", default=None, help="Destination directory for the .env.gz file.")
def pack_cmd(name: str, passphrase: str, dest: str | None) -> None:
    """Compress vault NAME into a .env.gz file."""
    try:
        out = compress_vault(name, passphrase, dest_dir=dest)
        click.echo(f"Compressed vault '{name}' → {out}")
    except CompressError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@compress_cmd.command("unpack")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, help="Passphrase for the restored vault.")
@click.option("--name", default=None, help="Override vault name when saving.")
def unpack_cmd(filepath: str, passphrase: str, name: str | None) -> None:
    """Decompress FILEPATH and restore the vault."""
    try:
        vault_name = decompress_vault(filepath, passphrase, dest_name=name)
        click.echo(f"Decompressed and saved as vault '{vault_name}'.")
    except CompressError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
