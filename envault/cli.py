"""Main CLI entry point for envault."""

import click

from envault.vault import save_vault, load_vault, list_vaults, _parse_env
from envault.cli_sync import export_cmd, import_cmd
from envault.cli_diff import diff_cmd


@click.group()
@click.version_option()
def cli() -> None:
    """envault — securely store and sync .env files."""


@cli.command("save")
@click.argument("vault_name")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True,
              confirmation_prompt=True, help="Encryption passphrase")
def save(vault_name: str, env_file: str, passphrase: str) -> None:
    """Encrypt and save an .env file into a named vault."""
    with open(env_file, "r") as fh:
        env_data = _parse_env(fh.read())

    save_vault(vault_name, env_data, passphrase)
    click.echo(f"Vault '{vault_name}' saved successfully.")


@cli.command("load")
@click.argument("vault_name")
@click.argument("output_file", type=click.Path())
@click.option("--passphrase", prompt=True, hide_input=True, help="Encryption passphrase")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite output file if it already exists")
def load(vault_name: str, output_file: str, passphrase: str, overwrite: bool) -> None:
    """Decrypt and write a vault to an .env file."""
    import os
    if not overwrite and os.path.exists(output_file):
        click.echo(
            f"Error: '{output_file}' already exists. Use --overwrite to replace it.",
            err=True,
        )
        raise SystemExit(1)

    try:
        env_data = load_vault(vault_name, passphrase)
    except FileNotFoundError:
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    with open(output_file, "w") as fh:
        for key, value in env_data.items():
            fh.write(f"{key}={value}\n")

    click.echo(f"Vault '{vault_name}' written to '{output_file}'.")


@cli.command("list")
def list_cmd() -> None:
    """List all saved vaults."""
    vaults = list_vaults()
    if not vaults:
        click.echo("No vaults found.")
        return
    for name in vaults:
        click.echo(f"  {name}")


cli.add_command(export_cmd, name="export")
cli.add_command(import_cmd, name="import")
cli.add_command(diff_cmd, name="diff")
