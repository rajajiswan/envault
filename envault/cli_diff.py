"""CLI commands for diffing vault contents."""

import click

from envault.vault import load_vault, _parse_env
from envault.diff import diff_envs


@click.command("diff")
@click.argument("vault_name")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase")
def diff_cmd(vault_name: str, env_file: str, passphrase: str) -> None:
    """Show differences between a vault and a local .env file."""
    try:
        vault_env = load_vault(vault_name, passphrase)
    except FileNotFoundError:
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error loading vault: {exc}", err=True)
        raise SystemExit(1)

    with open(env_file, "r") as fh:
        file_env = _parse_env(fh.read())

    result = diff_envs(vault_env, file_env)

    if not result.has_changes:
        click.echo("No differences found.")
        return

    click.echo(f"Diff between vault '{vault_name}' and '{env_file}':")
    click.echo(result.summary())
