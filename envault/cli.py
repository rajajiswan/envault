"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.vault import load_vault, save_vault, list_vaults, _parse_env
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


@click.group()
def cli():
    """envault — secure .env vault manager."""


@cli.command()
@click.argument("name")
@click.argument("env_file", type=click.Path(exists=True))
@click.password_option("--passphrase", prompt="Passphrase")
def save(name: str, env_file: str, passphrase: str):
    """Save an .env file into a named vault."""
    with open(env_file) as fh:
        raw = fh.read()
    env = _parse_env(raw)
    save_vault(name, env, passphrase)
    click.echo(f"Vault '{name}' saved.")


@cli.command()
@click.argument("name")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@click.option("--output", "-o", default=None, help="Write to file instead of stdout.")
def load(name: str, passphrase: str, output: str | None):
    """Load a vault and print its contents."""
    from envault.crypto import DecryptionError

    try:
        env = load_vault(name, passphrase)
    except DecryptionError:
        click.echo("Error: wrong passphrase or corrupted vault.", err=True)
        raise SystemExit(1)

    lines = "\n".join(f"{k}={v}" for k, v in env.items())
    if output:
        with open(output, "w") as fh:
            fh.write(lines + "\n")
        click.echo(f"Written to {output}.")
    else:
        click.echo(lines)


@cli.command("list")
def list_cmd():
    """List all saved vaults."""
    vaults = list_vaults()
    if not vaults:
        click.echo("No vaults found.")
    else:
        for v in vaults:
            click.echo(v)


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(diff_cmd, "diff")
cli.add_command(history_cmd, "history")
cli.add_command(tags_cmd, "tags")
cli.add_command(search_cmd, "search")
cli.add_command(audit_cmd, "audit")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(lock_cmd, "lock")
cli.add_command(backup_cmd, "backup")
cli.add_command(profile_cmd, "profile")
