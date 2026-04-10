"""CLI commands for vault backup and restore."""

import click

from envault.backup import BackupError, create_backup, delete_backup, list_backups, restore_backup


@click.group("backup")
def backup_cmd():
    """Manage vault backups."""


@backup_cmd.command("create")
@click.argument("vault_name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase.")
@click.option("--label", default=None, help="Optional snapshot label (default: timestamp).")
def create_cmd(vault_name, passphrase, label):
    """Create a backup snapshot of VAULT_NAME."""
    try:
        path = create_backup(vault_name, passphrase, label=label)
        click.echo(f"Backup created: {path}")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@backup_cmd.command("list")
@click.argument("vault_name")
def list_cmd(vault_name):
    """List all backups for VAULT_NAME."""
    backups = list_backups(vault_name)
    if not backups:
        click.echo(f"No backups found for '{vault_name}'.")
        return
    for b in backups:
        click.echo(f"  [{b['label']}]  {b['created']}  ({b['path']})")


@backup_cmd.command("restore")
@click.argument("vault_name")
@click.argument("label")
@click.option("--passphrase", prompt=True, hide_input=True, help="Vault passphrase.")
def restore_cmd(vault_name, label, passphrase):
    """Restore VAULT_NAME from backup LABEL."""
    try:
        restore_backup(vault_name, passphrase, label)
        click.echo(f"Vault '{vault_name}' restored from backup '{label}'.")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@backup_cmd.command("delete")
@click.argument("vault_name")
@click.argument("label")
def delete_cmd(vault_name, label):
    """Delete backup LABEL for VAULT_NAME."""
    try:
        delete_backup(vault_name, label)
        click.echo(f"Backup '{label}' deleted.")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
