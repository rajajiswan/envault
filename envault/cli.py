"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.crypto import DecryptionError
from envault.vault import list_vaults, load_vault, save_vault
from envault.cli_sync import export_cmd, import_cmd
from envault.cli_diff import diff_cmd
from envault.cli_history import history_cmd
from envault.cli_tags import tags_cmd
from envault.cli_search import search_cmd
from envault.cli_audit import audit_cmd
from envault.cli_rotate import rotate_cmd
from envault.cli_lock import lock_cmd
from envault.cli_backup import backup_cmd
from envault.cli_profile import profile_cmd
from envault.cli_merge import merge_cmd
from envault.cli_clone import clone_cmd


@click.group()
def cli() -> None:
    """envault — secure .env vault manager."""


@cli.command()
@click.argument("name")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, confirmation_prompt=True)
def save(name: str, env_file: str, passphrase: str) -> None:
    """Save an .env file into the vault."""
    with open(env_file) as fh:
        raw = fh.read()
    from envault.vault import _parse_env
    data = _parse_env(raw)
    save_vault(name, data, passphrase)
    click.echo(f"Vault '{name}' saved ({len(data)} key(s)).")


@cli.command()
@click.argument("name")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--output", "-o", default=None, type=click.Path())
def load(name: str, passphrase: str, output: str | None) -> None:
    """Load a vault and print or write the .env contents."""
    try:
        data = load_vault(name, passphrase)
    except DecryptionError:
        click.echo("Error: incorrect passphrase.", err=True)
        raise SystemExit(1)
    lines = "\n".join(f"{k}={v}" for k, v in data.items())
    if output:
        with open(output, "w") as fh:
            fh.write(lines + "\n")
        click.echo(f"Written to {output}.")
    else:
        click.echo(lines)


@cli.command(name="list")
def list_cmd() -> None:
    """List all stored vaults."""
    vaults = list_vaults()
    if not vaults:
        click.echo("No vaults found.")
    else:
        for v in vaults:
            click.echo(v)


cli.add_command(export_cmd, name="export")
cli.add_command(import_cmd, name="import")
cli.add_command(diff_cmd, name="diff")
cli.add_command(history_cmd, name="history")
cli.add_command(tags_cmd, name="tags")
cli.add_command(search_cmd, name="search")
cli.add_command(audit_cmd, name="audit")
cli.add_command(rotate_cmd, name="rotate")
cli.add_command(lock_cmd, name="lock")
cli.add_command(backup_cmd, name="backup")
cli.add_command(profile_cmd, name="profile")
cli.add_command(merge_cmd, name="merge")
cli.add_command(clone_cmd, name="clone")
