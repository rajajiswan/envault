"""CLI commands for vault locking."""

import click

from envault.lock import LockError, get_lock_info, is_locked, lock_vault, unlock_vault


@click.group("lock")
def lock_cmd():
    """Manage vault locks."""


@lock_cmd.command("on")
@click.argument("vault_name")
@click.option("--reason", "-r", default="", help="Optional reason for locking.")
def lock_on(vault_name: str, reason: str):
    """Lock a vault to prevent access."""
    try:
        info = lock_vault(vault_name, reason=reason)
        click.echo(f"Vault '{vault_name}' locked at {info['locked_at']}.")
        if reason:
            click.echo(f"Reason: {reason}")
    except LockError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lock_cmd.command("off")
@click.argument("vault_name")
def lock_off(vault_name: str):
    """Unlock a previously locked vault."""
    try:
        unlock_vault(vault_name)
        click.echo(f"Vault '{vault_name}' unlocked.")
    except LockError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lock_cmd.command("status")
@click.argument("vault_name")
def lock_status(vault_name: str):
    """Show lock status for a vault."""
    if is_locked(vault_name):
        info = get_lock_info(vault_name)
        click.echo(f"Vault '{vault_name}' is LOCKED.")
        click.echo(f"  Locked at : {info['locked_at']}")
        if info.get("reason"):
            click.echo(f"  Reason    : {info['reason']}")
    else:
        click.echo(f"Vault '{vault_name}' is unlocked.")
