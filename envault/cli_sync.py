"""CLI commands for vault sync (export/import)."""

import click
from envault.sync import export_vault, import_vault, SyncError


@click.command("export")
@click.argument("name")
@click.argument("output", type=click.Path())
@click.option(
    "--passphrase",
    prompt=True,
    hide_input=True,
    help="Passphrase used to encrypt the vault.",
)
def export_cmd(name: str, output: str, passphrase: str) -> None:
    """Export vault NAME to OUTPUT file as an encrypted snapshot."""
    try:
        export_vault(name, passphrase, output)
        click.echo(f"Vault '{name}' exported to {output}")
    except FileNotFoundError:
        click.echo(f"Error: vault '{name}' not found.", err=True)
        raise SystemExit(1)
    except SyncError as exc:
        click.echo(f"Export failed: {exc}", err=True)
        raise SystemExit(1)


@click.command("import")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--passphrase",
    prompt=True,
    hide_input=True,
    help="Passphrase used to decrypt the export.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing vault if it already exists.",
)
def import_cmd(input_file: str, passphrase: str, overwrite: bool) -> None:
    """Import an encrypted vault snapshot from INPUT_FILE."""
    try:
        name = import_vault(input_file, passphrase, overwrite=overwrite)
        click.echo(f"Vault '{name}' imported successfully.")
    except SyncError as exc:
        click.echo(f"Import failed: {exc}", err=True)
        raise SystemExit(1)
