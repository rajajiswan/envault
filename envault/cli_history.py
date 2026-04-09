"""CLI commands for vault history inspection."""

from __future__ import annotations

import click

from envault.history import load_history, clear_history, format_history
from envault.vault import list_vaults


@click.command("history")
@click.argument("vault_name")
@click.option("--clear", is_flag=True, default=False, help="Clear history for this vault.")
def history_cmd(vault_name: str, clear: bool) -> None:
    """Show (or clear) save history for VAULT_NAME."""
    known = list_vaults()
    if vault_name not in known:
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    if clear:
        clear_history(vault_name)
        click.echo(f"History cleared for vault '{vault_name}'.")
        return

    history = load_history(vault_name)
    click.echo(f"History for vault '{vault_name}':")
    click.echo(format_history(history))
