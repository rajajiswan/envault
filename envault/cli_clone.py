"""CLI commands for cloning vaults."""

from __future__ import annotations

import click

from envault.clone import CloneError, clone_vault
from envault.crypto import DecryptionError


@click.group("clone")
def clone_cmd() -> None:
    """Clone a vault under a new name."""


@clone_cmd.command("run")
@click.argument("source")
@click.argument("destination")
@click.option("--passphrase", prompt=True, hide_input=True, help="Source vault passphrase.")
@click.option(
    "--new-passphrase",
    default=None,
    hide_input=True,
    help="Passphrase for the cloned vault (defaults to source passphrase).",
)
def run_cmd(source: str, destination: str, passphrase: str, new_passphrase: str | None) -> None:
    """Clone SOURCE vault into a new DESTINATION vault."""
    if new_passphrase is None:
        new_passphrase = click.prompt(
            "Passphrase for cloned vault (leave blank to reuse source passphrase)",
            default="",
            hide_input=True,
            show_default=False,
        )
        if new_passphrase == "":
            new_passphrase = None

    try:
        result = clone_vault(source, destination, passphrase, new_passphrase)
    except DecryptionError:
        click.echo("Error: incorrect passphrase for source vault.", err=True)
        raise SystemExit(1)
    except CloneError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(
        f"Cloned '{result.source}' → '{result.destination}' "
        f"({result.key_count} key(s))."
    )
