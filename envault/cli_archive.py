"""CLI commands for vault archiving."""

import click

from envault.archive import ArchiveError, create_archive, extract_archive


@click.group("archive")
def archive_cmd():
    """Bundle and extract multiple vaults."""


@archive_cmd.command("create")
@click.argument("vaults", nargs=-1, required=True)
@click.option("--passphrase", prompt=True, hide_input=True, help="Shared passphrase for all vaults.")
@click.option("--output", "-o", default="envault_archive.json", show_default=True, help="Destination file path.")
def create_cmd(vaults, passphrase, output):
    """Create an archive from one or more vaults."""
    try:
        result = create_archive(list(vaults), passphrase, output)
        click.echo(f"Archived {result.count} vault(s) to '{result.archive_path}'.")
        for name in result.vaults:
            click.echo(f"  + {name}")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_cmd.command("extract")
@click.argument("archive_path")
@click.option("--passphrase", prompt=True, hide_input=True, help="Passphrase used to re-encrypt vaults.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vaults.")
def extract_cmd(archive_path, passphrase, overwrite):
    """Extract vaults from an archive file."""
    try:
        result = extract_archive(archive_path, passphrase, overwrite=overwrite)
        if result.count == 0:
            click.echo("No vaults extracted (all already exist; use --overwrite to replace).")
        else:
            click.echo(f"Extracted {result.count} vault(s) from '{archive_path}'.")
            for name in result.vaults:
                click.echo(f"  + {name}")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
