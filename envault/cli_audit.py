"""CLI commands for viewing and managing vault audit logs."""

import click
from envault.audit import load_audit_log, clear_audit_log, format_audit_log


@click.group("audit")
def audit_cmd():
    """View and manage vault access audit logs."""


@audit_cmd.command("show")
@click.argument("vault_name")
@click.option("--clear", is_flag=True, default=False, help="Clear the audit log after showing.")
def show_cmd(vault_name: str, clear: bool):
    """Show the audit log for VAULT_NAME."""
    entries = load_audit_log(vault_name)
    click.echo(format_audit_log(entries))
    if clear:
        clear_audit_log(vault_name)
        click.echo(f"Audit log for '{vault_name}' cleared.")


@audit_cmd.command("clear")
@click.argument("vault_name")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_cmd(vault_name: str):
    """Clear the audit log for VAULT_NAME."""
    clear_audit_log(vault_name)
    click.echo(f"Audit log for '{vault_name}' cleared.")


@audit_cmd.command("count")
@click.argument("vault_name")
def count_cmd(vault_name: str):
    """Show the number of audit entries for VAULT_NAME."""
    entries = load_audit_log(vault_name)
    click.echo(f"{len(entries)} audit entry/entries for '{vault_name}'.")
