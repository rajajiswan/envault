"""CLI commands for importing .env variables from external sources."""
from __future__ import annotations

import click

from envault.import_env import ImportEnvError, import_env


@click.group("import")
def import_cmd() -> None:
    """Import env variables into a vault from a file, URL, or stdin."""


@import_cmd.command("run")
@click.argument("vault_name")
@click.option("--passphrase", "-p", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option(
    "--source",
    "-s",
    default=None,
    help="Path to .env file, URL, or '-' for stdin (default: stdin).",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys in the vault.",
)
@click.option(
    "--key",
    "-k",
    "keys",
    multiple=True,
    help="Import only these keys (repeatable). Omit to import all.",
)
def run_cmd(
    vault_name: str,
    passphrase: str,
    source: str | None,
    overwrite: bool,
    keys: tuple[str, ...],
) -> None:
    """Import KEY=VALUE pairs into VAULT_NAME."""
    try:
        result = import_env(
            vault_name,
            passphrase,
            source,
            overwrite=overwrite,
            keys=list(keys) if keys else None,
        )
    except ImportEnvError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Vault : {result.vault_name}")
    click.echo(f"Source: {result.source}")
    click.echo(f"Imported : {result.total} key(s)")
    if result.keys_imported:
        for k in result.keys_imported:
            click.echo(f"  + {k}")
    if result.skipped:
        click.echo(f"Skipped  : {result.skipped} key(s) (use --overwrite to replace)")
        for k in result.keys_skipped:
            click.echo(f"  ~ {k}")
