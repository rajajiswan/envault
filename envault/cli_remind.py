"""CLI commands for managing vault reminders."""

from __future__ import annotations

import click
from datetime import datetime

from envault.remind import (
    RemindError,
    set_reminder,
    get_reminder,
    remove_reminder,
    list_reminders,
    is_due,
)


@click.group("remind")
def remind_cmd():
    """Manage reminders to review or rotate vault secrets."""


@remind_cmd.command("set")
@click.argument("vault")
@click.option("--days", required=True, type=int, help="Days until reminder is due.")
@click.option("--message", default="", help="Optional reminder message.")
def set_cmd(vault: str, days: int, message: str):
    """Set a reminder for VAULT."""
    try:
        due = set_reminder(vault, days, message)
        click.echo(f"Reminder set for '{vault}' — due {due.strftime('%Y-%m-%d %H:%M')} UTC.")
    except RemindError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@remind_cmd.command("status")
@click.argument("vault")
def status_cmd(vault: str):
    """Show reminder status for VAULT."""
    entry = get_reminder(vault)
    if entry is None:
        click.echo(f"No reminder set for '{vault}'.")
        return
    due_dt = datetime.fromisoformat(entry["due"])
    overdue = " (OVERDUE)" if is_due(vault) else ""
    click.echo(f"Due: {due_dt.strftime('%Y-%m-%d %H:%M')} UTC{overdue}")
    if entry["message"]:
        click.echo(f"Message: {entry['message']}")


@remind_cmd.command("remove")
@click.argument("vault")
def remove_cmd(vault: str):
    """Remove a reminder for VAULT."""
    removed = remove_reminder(vault)
    if removed:
        click.echo(f"Reminder for '{vault}' removed.")
    else:
        click.echo(f"No reminder found for '{vault}'.")


@remind_cmd.command("list")
def list_cmd():
    """List all reminders."""
    reminders = list_reminders()
    if not reminders:
        click.echo("No reminders set.")
        return
    for vault, entry in reminders.items():
        due_dt = datetime.fromisoformat(entry["due"])
        flag = " [OVERDUE]" if datetime.utcnow() >= due_dt else ""
        msg = f" — {entry['message']}" if entry["message"] else ""
        click.echo(f"{vault}: {due_dt.strftime('%Y-%m-%d')} UTC{flag}{msg}")
