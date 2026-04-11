"""Main CLI entry point for envault."""

import click

from envault.vault import save_vault, load_vault, list_vaults
from envault.crypto import DecryptionError
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
from envault.cli_compare import compare_cmd


@click.group()
@click.version_option()
def cli():
    """envault — securely store and sync .env files."""


@cli.command("save")
@click.argument("name")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, confirmation_prompt=True)
def save(name: str, env_file: str, passphrase: str):
    """Save an .env file into a named vault."""
    with open(env_file) as f:
        raw = f.read()

    from envault.vault import _parse_env
    data = _parse_env(raw)
    save_vault(name, data, passphrase)
    click.echo(f"Vault '{name}' saved with {len(data)} key(s).")


@cli.command("load")
@click.argument("name")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--output", "-o", default=".env", show_default=True, help="Output file path.")
def load(name: str, passphrase: str, output: str):
    """Load a vault and write it to an .env file."""
    try:
        data = load_vault(name, passphrase)
    except DecryptionError:
        raise click.ClickException("Decryption failed: wrong passphrase or corrupted vault.")
    except FileNotFoundError:
        raise click.ClickException(f"Vault '{name}' not found.")

    with open(output, "w") as f:
        for key, value in data.items():
            f.write(f"{key}={value}\n")

    click.echo(f"Vault '{name}' loaded to '{output}' ({len(data)} key(s)).")


@cli.command("list")
def list_cmd():
    """List all saved vaults."""
    vaults = list_vaults()
    if not vaults:
        click.echo("No vaults found.")
        return
    for v in vaults:
        click.echo(f"  - {v}")


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
cli.add_command(merge_cmd, "merge")
cli.add_command(clone_cmd, "clone")
cli.add_command(compare_cmd, "compare")
